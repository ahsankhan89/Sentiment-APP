import re
import time
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

## Defining Sentiment Automationid Api Header
def update_status(status):
    requests.post('http://localhost:1000/update_status', json={"status": status})

headers = {
'User-Agent': 'My User Agent 1.0',
'Content-Type': 'application/x-www-form-urlencoded',  # Specify content type as form-encoded
}

url = "https://art.artisticmilliners.com:8081/ords/art/sentiment/sentiment_automation_id"

try:
    response = requests.get(url, headers=headers , verify=False)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
    artautomationid = data['items'][0]["nvl(max(d.artautomationid),0)+1"]
    print(artautomationid)
except requests.exceptions.HTTPError as e:
    print("HTTP Error:", e)
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)

## Return Current Date
try:
    def get_current_date():
        current_date = datetime.now()
        formatted_date = current_date.strftime("%m/%d/%Y").lstrip("0").replace("/0", "/")
        return formatted_date

except Exception as er:
    print(er)
update_status("")
def selenium_code(url):
    """

    :param url:
    :return: df
    """

    update_status("Scraping Data, don't close window")
    ## for getting item information
    def extract_number(string):
        parts = string.split(":")
        if len(parts) > 1:
            return parts[1].strip()
        else:
            return ''

    service = Service()
    # Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print('driver initiated')
    # Open the website
    driver.get(url)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Maximize the browser window
    driver.maximize_window()
    time.sleep(2)

    product_title = driver.find_element(By.XPATH, "//h1[@data-test='product-title']").text

    time.sleep(2)



    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        specification = driver.find_element(By.XPATH, "//div[@data-test='@web/site-top-of-funnel/ProductDetailCollapsible-Specifications']//button[@type='button']")
        time.sleep(2)
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", specification)
        time.sleep(1)
        specification.click()
        time.sleep(1)

        tcin_number_string = driver.find_element(By.XPATH, "//body[1]/div[1]/div[2]/main[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[13]").text
        upc_number_string  =  driver.find_element(By.XPATH, "//body[1]/div[1]/div[2]/main[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[14]").text
        item_number_string =  driver.find_element(By.XPATH, "//body[1]/div[1]/div[2]/main[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[15]").text

        shipping_and_returns = driver.find_element(By.XPATH, "//div[@data-test='@web/site-top-of-funnel/ProductDetailCollapsible-ShippingReturns']//button[@type='button']")
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", shipping_and_returns)

        tcin_number = extract_number(tcin_number_string)
        upc_number = extract_number(upc_number_string)
        item_number = extract_number(item_number_string)
        print(tcin_number,'tcin number')
        print(upc_number,'upc number')
        print(item_number,'item number')

        # time.sleep(1)
        # move_to_specification = driver.find_element(By.XPATH, "//div[@data-test='@web/site-top-of-funnel/ProductDetailCollapsible-Specifications']")
        # driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", move_to_specification)



    except (NoSuchElementException, TimeoutException):
        print('No  Item  Detail Found')

    time.sleep(1)
    driver.execute_script("window.scrollBy(0, -2500);")




    time.sleep(1)

    try:
        click_drop_down = driver.find_element(By.XPATH,
                                              "//div[@id='above-the-fold-information']//span[@class='h-margin-l-tiny "
                                              "h-display-flex']//*[name()='svg']")
        click_drop_down.click()
    except (NoSuchElementException, TimeoutException):
        print('No drop Down  button found or the button is not clickable')
    time.sleep(3)
    try:
        click_on_All_reviews = driver.find_element(By.XPATH, "//span[@class='h-text-grayDarkest']")
        click_on_All_reviews.click()
    except (NoSuchElementException, TimeoutException):
        print('No All reviews  button found or the button is not clickable')

    time.sleep(2)

    try:
        move_to_footer = driver.find_element(By.XPATH, "//div[@class='h-text-center h-padding-v-tight']")
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", move_to_footer)
    except (NoSuchElementException, TimeoutException):
        print('No Footer class  found')

    time.sleep(2)
    # click on load More Button

    reviews_card_child_div = []
    total_comments_collected = 0

    # Collect all reviews available on the page

    for i in range(100):
        try:
            click_on_load_more = driver.find_element(By.XPATH,
                                                     "//button[@class='sc-ec9d3516-0 sc-e6042511-0 liBVMT ibmrHV']")
            print(click_on_load_more.text, 'button text')

            # Extract the number from the button text
            load_btn_number = click_on_load_more.text
            btn_number = int(re.findall(r'\d+', load_btn_number)[0])
            print(btn_number, 'btn_number')

            # Click the "Load More" button
            click_on_load_more.click()
        except (NoSuchElementException, TimeoutException):
            print('No "Load 8 More" button found')
            break  # Exit the loop if no button is found

        time.sleep(3)

        try:
            move_to_footer = driver.find_element(By.XPATH, "//div[@class='h-text-center h-padding-v-tight']")
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });",
                                  move_to_footer)
        except (NoSuchElementException, TimeoutException):
            print('No footer class found')

        # Calculate and collect comment divs
        while True:
            s = total_comments_collected + 1  # Start from the last collected comment + 1
            try:
                review_xpath = f"(//div[@class='h-margin-t-default h-text-md'])[{s}]"
                review_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, review_xpath))
                )
                ratings = driver.find_element(By.XPATH, f"(//span[@class='sc-13bc4695-0 Ruoxe'])[{s}]").text
                reviewer_name = driver.find_element(By.XPATH, f"(//span[@data-test='review-card--username'])[{s}]").text
                date_posted = driver.find_element(By.XPATH, f"(//span[@data-test='review-card--reviewTime'])[{s}]").text
                try:
                    recommendation = driver.find_element(By.XPATH, f"(//span[@aria-hidden='true'][normalize-space()='Would recommend'])[1]").text
                except NoSuchElementException:
                    recommendation = 'null'

                review_text = review_element.text
                ## get current date from function
                sentiment_date = get_current_date()
                # ratings = rating_xpath.text
                reviews_card_child_div.append({'review': review_text,
                                               'rating': ratings,
                                               'reviewer_name': reviewer_name,
                                               'Date_posted': date_posted,
                                                'Product_title': product_title,
                                                'tcin_number': tcin_number,
                                                'upc_number':upc_number,
                                                'item_number':item_number,
                                                 'artautomationid':artautomationid,
                                                'sentiment_date':sentiment_date,
                                                'recommendation':recommendation
                                               })

                print(
                      f"Product_title: {product_title}",
                      f"tcin_number: {tcin_number}",
                      f"Review: {review_text}",
                      f"Rating: {ratings}",
                      f"Reviewer_name:{reviewer_name}",
                      f"Date_posted:{date_posted}"

                      )

                total_comments_collected += 1
            except (NoSuchElementException, TimeoutException):
                print('No more reviews found')
                break

    df = pd.DataFrame(reviews_card_child_div)
    print("DataFrame head:", df.head())
    csv_file_name = 'reviews.csv'
    df.to_csv(csv_file_name, index=False)
    driver.quit()
    update_status("Scraping Done")
    return df


# selenium_code("https://www.target.com/p/men-s-slim-fit-jeans-goodfellow-co/-/A-78653190?preselect=79362800#lnk=sametab")