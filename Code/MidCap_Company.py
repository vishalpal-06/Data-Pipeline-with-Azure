from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import yaml
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r'..\Log\MidCap_screener_scraping.log'),
        logging.StreamHandler()  # This will also log to console
    ]
)
logger = logging.getLogger(__name__)

logger.info("Scraping Process Started for MidCap Companies")

# Setup Selenium WebDriver
service = Service(r'..\chromedriver.exe')
chrome_options = Options()
chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(service=service, options=chrome_options)

# Open Screener Website and login
driver.get('https://www.screener.in/')
driver.find_element(By.XPATH, '/html/body/nav/div[2]/div/div/div/div[2]/div[2]/a[1]').click()

# Load credentials from Config.yaml
with open(r'..\Config.yaml', 'r') as configuration:
    config = yaml.load(configuration, Loader=yaml.SafeLoader)

# Perform login
driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/div[1]/input').send_keys(config['Screener']['id'])
driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/div[2]/input').send_keys(config['Screener']['pass'])
driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/button').click()
time.sleep(5)  # Wait for login to complete
logger.info("Successfully logged into Screener.in")

# Base URL for pagination
base_url = "https://www.screener.in/screen/raw/?sort=&order=&source_id=&query=Market+Capitalization+%3E%3D+5000+AND%0D%0A+Market+Capitalization+%3C+20000&page="

# Initialize the final DataFrame
file_df = pd.DataFrame(columns=[
    "Serial_Number", "Company_Name", "Current_Market_Price_Rs", "Price_to_Earnings_Ratio",
    "Market_Capitalization_Rs_Cr", "Dividend_Yield_Percentage", "Net_Profit_Quarter_Rs_Cr",
    "Quarterly_Profit_Variation_Percentage", "Sales_Quarter_Rs_Cr",
    "Quarterly_Sales_Variation_Percentage", "Return_on_Capital_Employed_Percentage"
])

# Loop through pages
for page_number in range(1, 100):  # Assuming up to 100 pages or until no new data
    url = f"{base_url}{page_number}"
    driver.get(url)
    time.sleep(3)  # Allow page to load

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the table containing the data
    table = soup.find('table', class_='data-table')
    if not table:
        logger.warning(f"No table found on page {page_number}. Stopping pagination.")
        break

    # Initialize data dictionary for the current page
    data = {
        "Serial_Number": [],
        "Company_Name": [],
        "Current_Market_Price_Rs": [],
        "Price_to_Earnings_Ratio": [],
        "Market_Capitalization_Rs_Cr": [],
        "Dividend_Yield_Percentage": [],
        "Net_Profit_Quarter_Rs_Cr": [],
        "Quarterly_Profit_Variation_Percentage": [],
        "Sales_Quarter_Rs_Cr": [],
        "Quarterly_Sales_Variation_Percentage": [],
        "Return_on_Capital_Employed_Percentage": []
    }

    # Extract rows from the table body
    rows = table.find('tbody').find_all('tr')

    # Flag to check if we have any data on this page
    has_data = False

    for row in rows:
        if row.find('th'):
            continue

        cols = row.find_all('td')
        if not cols:
            continue

        if len(cols) != 11:
            continue

        data["Serial_Number"].append(cols[0].text.strip())
        data["Company_Name"].append(cols[1].text.strip())
        data["Current_Market_Price_Rs"].append(cols[2].text.strip())
        data["Price_to_Earnings_Ratio"].append(cols[3].text.strip())
        data["Market_Capitalization_Rs_Cr"].append(cols[4].text.strip())
        data["Dividend_Yield_Percentage"].append(cols[5].text.strip())
        data["Net_Profit_Quarter_Rs_Cr"].append(cols[6].text.strip())
        data["Quarterly_Profit_Variation_Percentage"].append(cols[7].text.strip())
        data["Sales_Quarter_Rs_Cr"].append(cols[8].text.strip())
        data["Quarterly_Sales_Variation_Percentage"].append(cols[9].text.strip())
        data["Return_on_Capital_Employed_Percentage"].append(cols[10].text.strip())

        has_data = True

    if not has_data:
        logger.info(f"No more data found on page {page_number}. Stopping pagination.")
        break

    # Create a DataFrame for the current page
    page_df = pd.DataFrame(data)

    # Check for duplicates based on Company_Name
    new_data = page_df[~page_df['Company_Name'].isin(file_df['Company_Name'])]

    if new_data.empty:
        logger.info(f"No new companies found on page {page_number}. Stopping pagination.")
        break

    # Append the new data to the final DataFrame
    file_df = pd.concat([file_df, new_data], ignore_index=True)
    logger.info(f"Processed page {page_number}. Total companies: {len(file_df)}")

# Save the final DataFrame to a CSV file
file_df.to_csv(r'../Data/Mid_Cap.csv', index=False)
logger.info(f"Scraping complete. Data saved to 'Mid_Cap.csv'. Total companies scraped: {len(file_df)}")
logger.info("Scraping Process Completed for MidCap Companies")
# Close the WebDriver
driver.quit()