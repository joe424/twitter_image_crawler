#coding=utf-8
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import pickle
import time
import html
import os
from selenium.webdriver.chrome.options import Options

###################################
#   create/select store folder and path
###################################
path = input("Input folder name: ")
path = "./" + path
if not os.path.exists(path): os.makedirs(path)
addr = input("Input URL: ")

###################################
#   set driver and load
###################################
chrome_options = Options()
chrome_options.add_argument("start-maximized")
driver = webdriver.Chrome(r'.\chromedriver.exe', options=chrome_options)
driver.get(addr)


###################################
#   cookie issue
###################################
driver.delete_all_cookies()
with open(r'.\my_cookie','rb') as f:
    cookies = pickle.load(f)
for cookie in cookies:
    if 'expiry' in cookie:
        del cookie['expiry']
    driver.add_cookie(cookie)


###################################
#   get started
###################################
driver.get(addr)
time.sleep(10)


###################################
#   analysis the html
###################################
max_position = -1000
last_position = -1000
failed_list = []
set_timer = False

while(1):
    soup = BeautifulSoup(driver.page_source, "lxml")
    time.sleep(2)
    tweet = soup.find_all(attrs={"data-testid": "tweet"})
    for i in tweet:
        ###################################
        #   collect data
        ###################################
        try:
            # get position
            style_text = str(i.find_parent(style=re.compile("^position: absolute")).get('style'))
            position = style_text[style_text.find("(") + 1 : style_text.find("px")]
            #print(position)
            if float(position) <= float(max_position):
                continue
            else:
                max_position = float(position)
            # get time 
            created_time = str(i.find("time").get("datetime"))[:-5].replace(":", "-")
            #print(created_time)

            # get img(s) link
            img_list = []

            orig_list = i.find_all("img")
            #orig_list = i.find_all("img")[1:]

            # only want the img's link same as the regex
            for j in range(len(orig_list)):
                if re.search("https\:\/\/pbs.twimg\.com\/media\/.+\?format=.+\&name=.+", orig_list[j].get("src")) != None:
                    img_list.append(orig_list[j].get("src"))

            if len(img_list) == 0:
                continue
            elif len(img_list) >= 4 and len(img_list) <= 7:
                img_list[1], img_list[2] = img_list[2], img_list[1]
            elif len(img_list) == 8:
                img_list[1], img_list[2] = img_list[2], img_list[1]
                img_list[5], img_list[6] = img_list[6], img_list[5]
            elif len(img_list) >= 1 and len(img_list) <= 3:
                pass
            #print(img_list)
        
        except:
            print("----------------------------------")
            print("error when analysis data")
            try:
                print(img_list)
                #print(orig_list)
            except:
                pass
            continue

        ###################################
        #   convert to img
        ###################################
        try:
            # get the orig link, and name the img name
            for i in range(len(img_list)):
                img_orig_url = img_list[i][: img_list[i].find("&name=") + 6] + "orig"
                img_name = img_orig_url[img_orig_url.find("media/") + 6 : img_orig_url.find("?format")]
                extension = "." + img_orig_url[img_orig_url.find("?format") + 8 : img_orig_url.find("&name=")]
                if len(img_list) != 1:
                    img_name = created_time + "-(" + str(i+1) + ")-" + img_name + extension
                else:
                    img_name = created_time + "-" + img_name + extension
                #print(img_name)
                #print(img_list)
                #print(img_orig_url)
                # create folder in path depend on year
                year = str(created_time[:4])
                if not os.path.exists(path + '\\' + year): os.makedirs(path + '\\' + year)

                if os.path.isfile(path + '\\' + year + '\\' + img_name): 
                    #print("file exist")
                    continue

                # set timer to prevent stucking in while
                timer = time.perf_counter()
                while(not os.path.isfile(path + '\\' + year + '\\' + img_name)):
                    urlretrieve(img_orig_url, path + '\\' + year + '\\' + img_name)
                    if time.perf_counter() - timer > 10:
                        print("----------------------------------")
                        print("failed: " + img_orig_url)
                        failed_list.append([img_orig_url, year, img_name])
                        break
        except:
            print("----------------------------------")
            print("error when convert to img")
            try:
                print(created_time)
            except:
                pass
            continue

    # set a timer
    if set_timer == False:
        t0 = time.perf_counter()
        set_timer = True
    
    # if the windows' position stop about 1min, then finish
    if last_position == max_position:
        if time.perf_counter() - t0 > 60:
            break

    if last_position != max_position:
        #print("reset timer")
        t0 = time.perf_counter() # restart timer
    last_position = max_position

    # scroll down the windows' position
    script = "window.scrollTo(0," + str(max_position) + ")"
    driver.execute_script(script) 
    time.sleep(2)

# try capture failed img again 
for i in range(len(failed_list)):
    try:
        print("try capture failed img again: ", failed_list[i][2])
        urlretrieve(failed_list[i][0], path + '\\' + failed_list[i][1] + '\\' + failed_list[i][2])
    except:
        print("failed: " + failed_list[i][0])
    if os.path.isfile(path + '\\' + failed_list[i][1] + '\\' + failed_list[i][2]):
        print("<Success>", failed_list[i][0])
    else:
        print("<Failed Again...>", failed_list[i][0])
driver.close()
print("Done")