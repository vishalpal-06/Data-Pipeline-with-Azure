from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import time 
import json

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service = service)

#-- Open Linkedin Website and login
driver.get('https://www.screener.in/')
driver.find_element(by=By.XPATH, value='/html/body/nav/div[2]/div/div/div/div[2]/div[2]/a[1]').send_keys(Keys.ENTER)
driver.find_element(by=By.XPATH, value='/html/body/main/div[2]/div[2]/form/div[1]/input').send_keys('vishalpal622003@gmail.com')
driver.find_element(by=By.XPATH, value='/html/body/main/div[2]/div[2]/form/div[2]/input').send_keys('Z*q8QAZ!YNbxcCH')
driver.find_element(by=By.XPATH, value='/html/body/main/div[2]/div[2]/form/button').send_keys(Keys.ENTER)

driver.get('https://www.screener.in/screen/raw/?sort=&order=&source_id=&query=Market+Capitalization+%3E+100%0D%0AAND%0D%0AMarket+Capitalization+%3C+200&page=2')


soap=BeautifulSoup(driver.page_source,'html.parser')



Serial_Number = []
Company_Name = []
for i in range(0,len(soap.find_all('td',class_='text'))):
  if i%2 != 0:
    Company_Name.append(soap.find_all('td',class_='text')[i].text)
  else:
    Serial_Number.append(soap.find_all('td',class_='text')[i].text)



columns_data = {f'Column {i+1}': [] for i in range(9)}
for i in range(len(soap.find_all('td',class_=""))):
  column_index = i % 9
  columns_data[f'Column {column_index+1}'].append(soap.find_all('td',class_="")[i].text)


data = list(zip(Serial_Number, Company_Name, columns_data['Column 1'], columns_data['Column 2'],
                columns_data['Column 3'], columns_data['Column 4'], columns_data['Column 5'],
                columns_data['Column 6'], columns_data['Column 7'],
                columns_data['Column 8'], columns_data['Column 9']))

columns = [
    "Serial_Number", "Company_Name", "Current_Market_Price_Rs", "Price_to_Earnings_Ratio", "Market_Capitalization_Rs_Cr",
    "Dividend_Yield_Percentage", "Net_Profit_Quarter_Rs_Cr", "Quarterly_Profit_Variation_Percentage", "Sales_Quarter_Rs_Cr",
    "Quarterly_Sales_Variation_Percentage", "Return_on_Capital_Employed_Percentage"
]



df = pd.DataFrame(data, columns=columns)
df.to_csv('second_50_records.csv', index=False)