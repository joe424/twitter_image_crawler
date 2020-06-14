#coding=utf-8
from selenium import webdriver
import pickle
import time

driver = webdriver.Chrome(r'.\chromedriver.exe')
driver.get('https://twitter.com/')
print("Enter your twitter account and password to save cookie")
print("wait 30 seconds to save cookie")
time.sleep(30)

cookies = driver.get_cookies()
with open(r'.\my_cookie','wb') as f:
    pickle.dump(cookies,f)
print ('done')
driver.close()