from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time 
import json

service = Service('C:\\Users\\Vishal-ardent\\OneDrive - Ardent\\Desktop\\Code_Game\\Selenium\\chromedriver.exe')
driver = webdriver.Chrome(service = service)

#-- Open Linkedin Website and login
driver.get('https://linkedin.com')
driver.find_element(by=By.XPATH, value='/html/body/nav/div/a[2]').send_keys(Keys.ENTER)

with open('cred.json', 'r') as file:
    data = json.load(file)

driver.find_element(by=By.XPATH, value='//*[@id="username"]').send_keys(data.get("id"))
driver.find_element(by=By.XPATH, value='/html/body/div/main/div[2]/div[1]/form/div[2]/input').send_keys(data.get("pass"))
driver.find_element(by=By.XPATH, value='/html/body/div/main/div[2]/div[1]/form/div[4]/button').click()


search_input = driver.find_element(by=By.XPATH, value='/html/body/div[6]/header/div/div/div/div[1]/input')
search_input.send_keys('Azure Data Engineer')
search_input.send_keys(Keys.ENTER)

driver.find_element(by=By.XPATH, value='/html/body/div[5]/div[3]/div[2]/section/div/nav/div/ul/li[1]/button').click()

time.sleep(10)