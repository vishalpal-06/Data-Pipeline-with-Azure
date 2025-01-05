from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import yaml

# Setup Selenium WebDriver
service = Service('chromedriver.exe')
chrome_options = Options()
chrome_options.add_argument("--headless=new")


driver = webdriver.Chrome(service=service, options=chrome_options)

# Open Screener Website and login
driver.get('https://www.screener.in/')
#time.sleep(2)  # Wait for the page to load
driver.find_element(By.XPATH, '/html/body/nav/div[2]/div/div/div/div[2]/div[2]/a[1]').click()
#time.sleep(2)  # Allow login page to load
with open('gitignore\Config.yaml', 'r') as configuration:
    config = yaml.load(configuration, Loader=yaml.SafeLoader)

driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/div[1]/input').send_keys(config['Screener']['id'])
driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/div[2]/input').send_keys(config['Screener']['pass'])
driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/button').click()
#time.sleep(5)  # Wait for login to complete

# Base URL for pagination
base_url = "https://www.screener.in/screen/raw/?sort=&order=&source_id=&query=Market+Capitalization+%3C+5000&page="

# Initialize the final DataFrame
file_df = pd.DataFrame(columns=[
    "Serial_Number", "Company_Name", "Current_Market_Price_Rs", "Price_to_Earnings_Ratio",
    "Market_Capitalization_Rs_Cr", "Dividend_Yield_Percentage", "Net_Profit_Quarter_Rs_Cr",
    "Quarterly_Profit_Variation_Percentage", "Sales_Quarter_Rs_Cr",
    "Quarterly_Sales_Variation_Percentage", "Return_on_Capital_Employed_Percentage"
])

# Loop through multiple pages
for page_number in range(1, 100):  # Assuming 10 pages
    # Update the URL with the current page number
    url = f"{base_url}{page_number}"
    driver.get(url)
    time.sleep(3)  # Allow page to load

    # Parse the page content
    soap = BeautifulSoup(driver.page_source, 'html.parser')

    # Initialize lists to store Serial Numbers and Company Names
    Serial_Number = []
    Company_Name = []

    # Extract Serial Numbers and Company Names
    text_elements = soap.find_all('td', class_='text')
    for idx, element in enumerate(text_elements):
        if idx % 2 != 0:
            Company_Name.append(element.text.strip())
        else:
            Serial_Number.append(element.text.strip())

    # Initialize a dictionary for the column data
    columns_data = {f'Column {i + 1}': [] for i in range(9)}

    # Extract data for the columns
    column_elements = soap.find_all('td', class_="")
    for idx, element in enumerate(column_elements):
        column_index = idx % 9
        columns_data[f'Column {column_index + 1}'].append(element.text.strip())

    # Combine data into a list of tuples
    data = list(zip(
        Serial_Number,
        Company_Name,
        columns_data['Column 1'],
        columns_data['Column 2'],
        columns_data['Column 3'],
        columns_data['Column 4'],
        columns_data['Column 5'],
        columns_data['Column 6'],
        columns_data['Column 7'],
        columns_data['Column 8'],
        columns_data['Column 9']
    ))

    # Create a DataFrame for the current page
    df = pd.DataFrame(data, columns=file_df.columns)

    new_data = df[~df['Company_Name'].isin(file_df['Company_Name'])]
    
    if new_data.empty:
        break  # Stop if no new companies are found

    # Append the current DataFrame to the final DataFrame
    file_df = pd.concat([file_df, df], ignore_index=True)

    print(page_number)

# Save the final DataFrame to a CSV file
file_df.to_csv('Small_Cap.csv', index=False)

# Close the WebDriver
driver.quit()
