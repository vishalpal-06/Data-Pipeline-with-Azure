# screener_scraper_base.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import yaml
import logging
import os

class ScreenerScraper:
    """
    A base class for scraping financial data from Screener.in for different market caps
    (LargeCap, MidCap, SmallCap). Customizable via parameters for URL, log file, and CSV file.
    """

    def __init__(self, base_url, log_filename, csv_filename, market_cap_type):
        """
        Initialize the scraper with specific parameters.

        Args:
            base_url (str): The base URL for pagination (e.g., for LargeCap, MidCap, SmallCap).
            log_filename (str): Name of the log file (e.g., 'LargeCap_screener_scraping.log').
            csv_filename (str): Name of the CSV file (e.g., 'Large_Cap.csv').
            market_cap_type (str): Type of market cap (e.g., 'LargeCap', 'MidCap', 'SmallCap')
                                  for logging purposes.
        """
        # Configure logging
        log_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Log')
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        log_file_path = os.path.join(log_folder, log_filename)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path),
                logging.StreamHandler()  # Log to console as well
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Scraping Process Started for {market_cap_type} Companies")

        # Store parameters
        self.base_url = base_url
        self.csv_filename = csv_filename
        self.market_cap_type = market_cap_type

        # Setup Selenium WebDriver
        # chromedriver_path = os.path.join('..', 'chromedriver.exe')
        service = Service('chromedriver.exe')
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Login to Screener.in
        self.login()

    def login(self):
        """Handle the login process to Screener.in using credentials from Config.yaml."""
        self.driver.get('https://www.screener.in/')
        self.driver.find_element(By.XPATH, '/html/body/nav/div[2]/div/div/div/div[2]/div[2]/a[1]').click()

        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
        config_path = os.path.join(script_dir, "..", "Config.yaml")

        with open(config_path, 'r') as configuration:
            config = yaml.load(configuration, Loader=yaml.SafeLoader)

        # Perform login
        self.driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/div[1]/input').send_keys(
            config['Screener']['id'])
        self.driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/div[2]/input').send_keys(
            config['Screener']['pass'])
        self.driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/form/button').click()
        time.sleep(5)  # Wait for login to complete
        self.logger.info("Successfully logged into Screener.in")

    def scrape_data(self):
        """Scrape financial data from Screener.in based on the base URL."""
        # Initialize the final DataFrame with common columns
        file_df = pd.DataFrame(columns=[
            "Serial_Number", "Company_Name", "Current_Market_Price_Rs", "Price_to_Earnings_Ratio",
            "Market_Capitalization_Rs_Cr", "Dividend_Yield_Percentage", "Net_Profit_Quarter_Rs_Cr",
            "Quarterly_Profit_Variation_Percentage", "Sales_Quarter_Rs_Cr",
            "Quarterly_Sales_Variation_Percentage", "Return_on_Capital_Employed_Percentage"
        ])

        # Loop through pages
        for page_number in range(1, 100):  # Assuming up to 100 pages or until no new data
            url = f"{self.base_url}{page_number}"
            self.driver.get(url)
            time.sleep(3)  # Allow page to load

            # Parse the page content with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find the table containing the data
            table = soup.find('table', class_='data-table')
            if not table:
                self.logger.warning(f"No table found on page {page_number}. Stopping pagination.")
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
            has_data = False

            for row in rows:
                if row.find('th'):
                    continue

                cols = row.find_all('td')
                if not cols or len(cols) != 11:
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
                self.logger.info(f"No more data found on page {page_number}. Stopping pagination.")
                break

            # Create a DataFrame for the current page
            page_df = pd.DataFrame(data)

            # Check for duplicates based on Company_Name
            new_data = page_df[~page_df['Company_Name'].isin(file_df['Company_Name'])]

            if new_data.empty:
                self.logger.info(f"No new companies found on page {page_number}. Stopping pagination.")
                break

            # Append the new data to the final DataFrame
            file_df = pd.concat([file_df, new_data], ignore_index=True)
            self.logger.info(f"Processed page {page_number}. Total companies: {len(file_df)}")

        # Save the final DataFrame to a CSV file
        data_folder = os.path.join('..', 'Data')
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        csv_path = os.path.join(data_folder, self.csv_filename)
        file_df.to_csv(csv_path, index=False)
        self.logger.info(f"Scraping complete. Data saved to '{self.csv_filename}'. Total companies scraped: {len(file_df)}")

    def close(self):
        """Close the WebDriver to free up resources."""
        self.driver.quit()
        self.logger.info(f"Scraping Process Completed for {self.market_cap_type} Companies")

    def run(self):
        """Run the scraping process."""
        try:
            self.scrape_data()
        finally:
            self.close()


if __name__ == "__main__":
    print("This is a base module and should not be run directly. Please import ScreenerScraper "
          "into a specific scraper script (e.g., largecap_scraper.py) and configure it there.")