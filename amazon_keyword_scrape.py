#To run this script you should have a google sheet with name item keywords and item urls.
#The access of above 2 files should be shared with the email in cred file.
#this code will pick up the keyword from one file and scrape the products urls for that keyword
#and store the keyword and 10 urls in item url sheet.

#Libraries for selenium environment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

#To connect with google docs
import googleapiclient.discovery
import gspread
import pygsheets
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import webbrowser

# To detect language
import re
from datetime import date
import time
from datetime import datetime
import csv
import os
from random import randint
import random
import traceback

global client, credentials, scope, scraped_links, item_url, user_agents

user_agents = []
with open('user_agents2.csv', 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        user_agents.append(row[0])
        
run_local=False
def get_driver():
    # Select a random user agent
    user_agent = random.choice(user_agents)
    print("User Agent", user_agent)
    #Setting up driver for server run on server
    chrome_options = webdriver.ChromeOptions()
    #chrome_service = Service(ChromeDriverManager().install()) 
    chrome_options.add_argument(f"--user-agent={user_agent}")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    
    return driver
#This function gets a keyword as input and open the amazon url using selenium
#and search 10 keywords and get urls of the products with price greater than 25$
#and rating greater than 4.2 stars and reviews greater than 100.
def get_url(keyword):
    print("Keyword",keyword)
    amazon_url='https://www.amazon.com/?&tag=googleglobalp-20&ref=pd_sl_7nnedyywlk_e&adgrpid=82342659060&hvpone=&hvptwo=&hvadid=393493755082&hvpos=&hvnetw=g&hvrand=2256236398804460963&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9060976&hvtargid=kwd-10573980&hydadcr=2246_11061421'
    #Setting up browser for local run
    if(run_local):
        # Set up browser for scraping
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_service = Service('chromedriver')
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    #----------------------------------------------------------------------------- 
    #setup heroku
    if(not(run_local)):
        driver=get_driver()
        
    delay = randint(5, 20)  # Delay in seconds
    time.sleep(delay)
    print(delay)
    driver.get(amazon_url)
    #print("url source", driver.page_source)
    #input("URL i")
    delay = randint(1, 20)
    print(delay)
    time.sleep(delay)
    
    try:
        #Enter keyword in searchbar
        searchbox_xpath='//input[@id="twotabsearchtextbox"]'
        #wait = WebDriverWait(driver, 20)
        searchbox = driver.find_element(By.XPATH, searchbox_xpath)
        searchbox_search=searchbox.send_keys(keyword)
        searchbox.send_keys(Keys.RETURN)
        temp_page_source = driver.page_source
        #print("review page", temp_page_source)
        captcha_phrase = "To discuss automated access to Amazon data please contact api-services-support@amazon.com."
        search_url=driver.current_url
        if(captcha_phrase in temp_page_source):
            print("****************CAPTCHA AHEAD*******************")
            search_url=driver.current_url
            driver.quit()
            delay = randint(10, 20)
            time.sleep(delay)
            driver=get_driver()
            driver.get(current_url)
            
    except Exception as e:
        print("page source in search",driver.page_source)
        print("No searchbox",e, traceback.print_exc())
        driver.quit()
        delay = randint(10, 20)
        time.sleep(delay)
        get_url(keyword)
        return
    #time.sleep(delay)    
    observed_products=1
    # Variable to See 25 products
    total_products=25
    #Conditions/criteria to get the link and put in sheet.
    review_criteria=100
    price_criteria=24
    rating_criteria=4.2
    temp_dict={}
    #Iterate until 25 products have not been collected
    while(observed_products<total_products):
        try:
            if(not(run_local)):
                driver=get_driver()
                driver.get(search_url)
            #Get all box on the page and extract the price, reviews, rating and links
            #and match passing criteria, if they pass Store them in dictionary 
            
            print('url', driver.current_url)
            box_xpath = "//div[@data-component-type='s-search-result']/div[contains(@class, 'sg-col-inner')]/div"
            box_elements = driver.find_elements(By.XPATH, box_xpath)
            total_boxes = len(box_elements)
            print("Total Boxes", total_boxes)
            delay = randint(5, 20)
            time.sleep(delay)
            if(total_boxes==0 and "Sorry! Something went wrong!" in driver.page_source):
                print("page source in box",driver.page_source) 
                print("Captcha received trying again")
                driver.quit()
                delay = randint(5, 20)
                time.sleep(delay)
                get_url(keyword)
            #input("boxes")
            i=0
            #Go one by one on products and collect their information
            for features in box_elements:
                i=i+1
                #See if we have gathered 25 products
                if(observed_products<=total_products):
                    print("Observed products, total", observed_products, total_products)
                    try:
                        #Get number of reviews
                        reviews_number_xpath = './/span[@class="a-size-base s-underline-text"]'
                        review_element = features.find_element(By.XPATH, reviews_number_xpath)
                        review = review_element.text
                        print("Number of reviews", review)
                        review = (review.replace(',', ''))
                        #time.sleep(delay)
                        #if number of reviews are greater than 100 get its price
                        if(int(review)>review_criteria):
                            price_xpath = './/span[@class="a-price"]/span[1]'
                            price_element = features.find_element(By.XPATH, price_xpath)
                            price = price_element.get_attribute('textContent')
                            price = price[1:-3].strip()
                            print("price", price)
                            #time.sleep(delay)
                            #If price is greater than or equal to 24 then get its rating
                            if (int(price) >= price_criteria):
                                rating_xpath = './/span[@class="a-icon-alt"]'
                                rating_element = features.find_element(By.XPATH, rating_xpath)
                                rating = rating_element.get_attribute('textContent')
                                match = re.search(r"[0-9]+\.[0-9]", rating)
                                # Get the number
                                rating = match.group(0).strip()
                                print("rating", rating)
                                #time.sleep(delay)
                                #if rating is greaten than or equal to 4.2 then get link of products
                                if (float(rating) >= rating_criteria):
                                    link_xpath = './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]'
                                    link_element = features.find_element(By.XPATH, link_xpath)
                                    link = link_element.get_attribute('href')
                                    print("Link", link)
                                    #add link and review rating and price number in dictionary
                                    temp_dict[review]={"review": review,"link":link, "price":price, "rating":rating}
                                    observed_products=observed_products+1
                                    print("temp_dict", temp_dict)
                                    #time.sleep(delay)
                    except Exception as e:
                        #If anything is not available(price, reviewsare missing in some cases i.e sponsored) 
                        print("Missing Element")
            try:
                #If the first page doesnt have 25 eligible products then go to next page
                if(observed_products<=total_products):
                    #If there are less then 25 products on first page then get more products from next page.
                    next_page_xpath = '//span[@class="s-pagination-strip"]/a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]'
                    next_page_element = driver.find_element(By.XPATH, next_page_xpath)
                    driver.get(next_page_element.get_attribute('href'))
                    delay = randint(10, 20)
                    time.sleep(delay)
            except Exception as e:
                temp_page_source = driver.page_source
                #print("review page", temp_page_source)
                captcha_phrase = "To discuss automated access to Amazon data please contact api-services-support@amazon.com."
                if(captcha_phrase in temp_page_source):
                    print("****************CAPTCHA AHEAD*******************")
                    current_url=driver.current_url
                    driver.quit()
                    #delay = randint(10, 0)
                    time.sleep(10)
                    driver=get_driver()
                    driver.get(current_url)  
                else:
                    print("No next page exists")
                    driver.quit()
                    break
                
        except Exception as e:
            print("Please Try anyother keyword")
            driver.quit()
            
    today = datetime.today().strftime("%B %d, %Y")
    # Get the top 10 elements
    # Sort the dictionary items by keys in descending order and get the top required items
    
    #Variable to get 10 item links 
    required_items=10
    # sorted_items = sorted(temp_dict.items(), key=lambda x: int(x[0]), reverse=True)[:required_items]

    # Sort the dictionary based on keys in descending order and get the top 10 dictionaries
    top_dicts = dict(sorted(temp_dict.items(), key=lambda x: int(x[0]), reverse=True)[:required_items])
    print("top_dicts",top_dicts)
    # Extract the values of "review," "link," "price," and "rating" from each dictionary
    rows = [["review", "link", "price", "rating"]]
    for values in top_dicts.values():
        item_url.append_row([today, keyword, values["link"], values["review"], values["price"], values["rating"]])
        #rows.append(row)
    print("Sheet updated")
    driver.quit()
    return
    
#This function connects with googlesheets and gets keywords from a googlesheet and
#calls a function get_url with the input as keyword and make a list for those keywords
#that has been used.
def get_keywords():
    global client, credentials, scope,item_url
    # Connect to Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('cred.json', scope)
    client = gspread.authorize(credentials)

    # SHeet name where urls of all the items to be scraper are stores.
    spreadsheet = client.open('Item keywords')
    keywords_worksheet = spreadsheet.sheet1
    # Retrieve URLs from each row of the Google Sheet
    # Assuming URLs are in column A, starting from row 1
    keywords = keywords_worksheet.col_values(1)[0:]
    #print("keyword",keywords)
    item_url=client.open('Item keyword-URL')
    item_url=item_url.sheet1
    print("items",item_url.url)
    
    scraped_keywords=item_url.col_values(2)[0:]
    #print("keywords",scraped_keywords)
    # Iterate through each keyword and open it using Selenium
    for keyword in keywords:
        # search and get URL
        #print("in for")
        if (keyword not in scraped_keywords): #if keyword is not already scraped.
            #print("in if")
            get_url(keyword)
            print("I will wait 1 minute to get next keyword")
            time.sleep(60)
    
    return
    
def main():
    get_keywords()
    print("I have completed my scrapping")
    print("I will wait 3 minutes before running the script again")
    time.sleep(200)
    return


# #===============================================================================

if __name__ == "__main__":
    main()
