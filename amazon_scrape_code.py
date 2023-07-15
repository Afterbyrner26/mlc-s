#Libraries for selenium environment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#To connect with google docs
import googleapiclient.discovery
import gspread
import pygsheets
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import webbrowser

# To detect language
from langdetect import detect
import csv
import random
from datetime import date
import time
import os
from random import randint
import traceback

global client, credentials, scope, scraped_links, amazon_product_urls, user_agents


run_local = False
if(run_local):
    from seleniumwire import webdriver
else:
    from webdriver_manager.chrome import ChromeDriverManager
#-----------------------------------------------------------------------------


def get_driver():
    global user_agents
    user_agents = []
    with open('user_agents.csv', 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            user_agents.append(row[0])

    # Select a random user agent
    user_agent = random.choice(user_agents)
    print("User Agent", user_agent)
    
    #Setting up driver for server run on server
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--user-agent={user_agent}')        
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    
    return driver
#This functions gets a url scrape its title, About info, product description
#and 10 5-star reviews of customers make a google document and write everything
#in that document and then insert link of the document in a speadsheet file.
def scrape_url(link):
    #Setting up browser for local run
    if(run_local):
        # Set up browser for scraping
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_service = Service('chromedriver')
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    #----------------------------------------------------------------------------- 
    if(not(run_local)):
        driver=get_driver()
        delay = randint(10, 20)
        time.sleep(delay)
        
    driver.get(link)
    print("Link in driver",link)
    delay = randint(10, 20)
    time.sleep(delay)
    temp_page_source = driver.page_source
    captcha_phrase = "To discuss automated access to Amazon data please contact api-services-support@amazon.com."
    if(captcha_phrase in temp_page_source):
        print("****************CAPTCHA AHEAD0*******************")
        print("Page source", temp_page_source)
        driver.quit()
        driver=get_driver()
        driver.get(link)  
    # Product Title
    try:
        title_xpath = '//span[@id="productTitle"]'
        # Wait for the element to be visible
        wait = WebDriverWait(driver, 20)
        title = wait.until(EC.presence_of_element_located((By.XPATH, title_xpath)))
        # Get the text of the element
        title = title.text
        print("Title", title)
    except Exception as e:
        title = 'No title'
        print("Error in Getting title")
    
    # Get About Info   
    try:
        about_info_xpath = '//div[@id="feature-bullets"]/ul/li/span'
        #wait = WebDriverWait(driver, 20)
        #about_info = wait.until(EC.visibility_of_element_located((By.XPATH, about_info_xpath)))
        delay = randint(3, 10)
        time.sleep(delay)
        about_info = driver.find_elements(By.XPATH, about_info_xpath)
        about_text=''
        # Iterate over the list items and get the text of the span elements
        for list_item in about_info:
            span_elements = list_item.find_elements(By.XPATH, './span')
            about_text += list_item.text + '\n \n'
            print(about_text)
    except Exception as e:
        about_text="No About text Available"
        print("No about info")
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
    delay = randint(3, 10)
    time.sleep(delay)
    #Product Description
    try:
        product_description_xpath = "//div[@id='productDescription']"
        # wait = WebDriverWait(driver, 20)
        # product_description = wait.until(EC.presence_of_element_located((By.XPATH, product_description_xpath)))
        delay = randint(3, 10)
        time.sleep(delay)
        product_description = driver.find_element(By.XPATH, product_description_xpath)
        product_description = product_description.text
        print("product_description", product_description)
    except Exception as e:
        product_description = 'No Product Description'
        print("No product_description found")

    try:
        #Click on five star to filter 5-star reviews only
        five_star_xpath = '//*[@id="histogramTable"]/tbody/tr[1]/td[3]/span[2]/a'
        #time.sleep(60)
        wait = WebDriverWait(driver, 20)
        five_star_reviews = wait.until(EC.presence_of_element_located((By.XPATH, five_star_xpath)))
        five_star_reviews = driver.find_element(By.XPATH, five_star_xpath).click()
        
    except Exception as e:
        print("Could not get stars",e)
    number_of_reviews = 0
    reviews = ''
    req_review_lenght=400
    
    #While the number of reviews are less than 10
    while (number_of_reviews < 10):
        print("number_of_reviews", number_of_reviews)
        get_dynamic_xpath = 1
        temp_page_source = driver.page_source
        #print("review page", temp_page_source)
        captcha_phrase = "To discuss automated access to Amazon data please contact api-services-support@amazon.com."
        if(captcha_phrase in temp_page_source):
            current_url=driver.current_url
            driver.quit()
            driver=get_driver()
            driver.get(current_url)
            
        while (get_dynamic_xpath < 12 and number_of_reviews < 10):
            review_xpath = f'//div[5]/div[3]/div/div[{get_dynamic_xpath}]/div/div/div[4]/span/span'
            
            #review_xpath="//span[@data-hook='review-body']["+str(get_dynamic_xpath)+"]/span"
            print("REVIEW XPATH:",review_xpath)
            temp_page_source = driver.page_source
            #print("review page", temp_page_source)
            captcha_phrase = "To discuss automated access to Amazon data please contact api-services-support@amazon.com."
            if(captcha_phrase in temp_page_source):
                print("****************CAPTCHA AHEAD*******************")
                current_url=driver.current_url
                driver.quit()
                delay = randint(10, 20)
                time.sleep(delay)
                driver=get_driver()
                driver.get(current_url)
            get_dynamic_xpath = get_dynamic_xpath + 1
            
            try:    
                #time.sleep(20)
                wait = WebDriverWait(driver, 20)
                review = wait.until(EC.presence_of_element_located((By.XPATH, review_xpath)))
        
                #review = driver.find_element(By.XPATH, review_xpath)
                review = review.text
                print("review",review)
                language = detect(review)
                if (language == 'en' and len(str(review)) >= req_review_lenght):
                    reviews = reviews + str(review) + '\n \n /// \n \n'
                    number_of_reviews = number_of_reviews + 1
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
                    print("Error getting review")
                    review = ''
                
        # if there are less than 10 reviews yet then click on next page to get more reviews.
        try:
            next_page_xpath = '//*[@id="cm_cr-pagination_bar"]/ul/li[2]/a'
            # Click on the link
            wait = WebDriverWait(driver, 20)
            next_page = wait.until(EC.visibility_of_element_located((By.XPATH, next_page_xpath)))
            driver.get(next_page.get_attribute('href'))
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
                break
    if(title!="No title"):
        # Create a service object for the Google Drive API.
        drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)
        
        # Specify the ID of the destination folder in Google Drive
        folder_id = '13aXyBoI2V2MOiowptJW-TjbDYiRMq4oE'
        
        
        # Create a new Google Doc in folder.
        item_docs_metadata = {
            'name': title,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.document'
        }
        item_docs = drive_service.files().create(body=item_docs_metadata, fields='id,webViewLink').execute()

        # Get the ID and link of the new Google Doc.
        item_doc_id = item_docs['id']
        item_doc_link = item_docs['webViewLink']
        
        # Create a service object for the Google Docs API.
        docs_service = googleapiclient.discovery.build('docs', 'v1', credentials=credentials)
        content = f" - Details - \n \n Amazon title :  {title}  \n \n - Link - \n {link} \n \n - About this Item -\n \n {about_text} \n \n - Product Description - \n \n {product_description} \n \n  - Reviews -\n \n {reviews} \n"
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': content,
                }
            }
        ]

        docs_service.documents().batchUpdate(documentId=item_doc_id, body={'requests': requests}).execute()
        
        print("Docs_link",item_doc_link)
        today = date.today().strftime('%Y-%m-%d')
        # Create a list of values to update in the range
        values = [today, today, link, item_doc_link, title]
        
        # Update the values in the specified range
        amazon_product_urls.append_row(values)
    driver.quit()
    return


def make_connections():
    global client, credentials, scope,amazon_product_urls
    # Connect to Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('cred.json', scope)
    client = gspread.authorize(credentials)

    # SHeet name where urls of all the items to be scraper are stores.
    Item_urls = client.open('Item URL')
    worksheet = Item_urls.sheet1
    amazon_product_urls=client.open('Amazon Product URLs')
    amazon_product_urls=amazon_product_urls.sheet1
    
    # Retrieve URLs from each row of the Google Sheet
    # Assuming URLs are in column A, starting from row 1
    links = worksheet.col_values(1)[0:]
    scraped_links=amazon_product_urls.col_values(3)[0:]
    # Iterate through each link and open it using Selenium
    for link in links:
        # Open the URL using Selenium
        if (link not in scraped_links): #if link is not already scraped.
            print("Link",link)
            scrape_url(link)
            print("Waiting a minute before next link")
            time.sleep(60)
    return


def main():
    while(True):
        make_connections()
        print("Waiting 5minutes")
        time.sleep(300)
    print("I have completed my scrapping")


# #===============================================================================

if __name__ == "__main__":
    main()