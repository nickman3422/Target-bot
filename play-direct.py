import time
from selenium import webdriver
import requests
import json
from multiprocessing.dummy import Pool
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from playsound import playsound
from datetime import datetime
'''
ideas:
create new account everytime you checkout
use that proxy finder that was made for csec380 and use those proxies 
'''
# options = webdriver.ChromeOptions()
# options.add_argument('user-data-dir=C:\Users\nickm\AppData\Local\Google\Chrome\User Data\Profile') #Path to your chrome profile
# w =webdriver.Chrome(executable_path="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", chrome_options=options)
'''
#threading:
def test(i):
    driver = webdriver.Chrome('C:\\Users\\nickm\\Downloads\\chromedriver_win32\\chromedriver')
    driver.get('https://target.com')
    print("here1")
    driver.get('https://target.com')
    driver.get("https://login.target.com/gsp/static/v1/login/?client_id=ecom-web-1.0.0&ui_namespace=ui-default&back_button_action=browser&keep_me_signed_in=true&kmsi_default=false&actions=create_session_signin")
    print("here")
    time.sleep(5) # Let the user actually see something!
    time.sleep(5) # Let the user actually see something!
    print(i, " finished")
    driver.quit()
p = Pool(5)                   #The start of the threading magic
p.map(test,range(5))  #Without threading, it takes way too long to run
p.close()
p.join()
'''


def get_keys(product_url):
    response = requests.get(product_url)
    apikey = str(response.text).split("apiKey")[1].split('"')[2]
    tcin = str(response.text).split("sku")[1].split('"')[2]
    return apikey, tcin
def checkifcheckedout(req,apikey):
    headers = {'Host': 'carts.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '209',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Origin': 'https://www.target.com',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': 'https://www.target.com/co-cart',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {'cart_type': 'SFL', 'field_groups': 'CART,CART_ITEMS,SUMMARY', 'key': apikey}
    response = req.get('https://carts.target.com/web_checkouts/v1/cart?',params=parmas)
    print("____checking if checkout has successful_______")
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended checking checkout_______")
    if ('"items_quantity":0' not in str(response.text)):
        print("checkout worked")
        return True
    else:
        print("checkout did not work")
        return False

def checkifinstock(product_urls):
    i = 0
    instock = False
    while instock is False:
        for url in product_urls:
            time.sleep(1)
            apikey, product_tcin = get_keys(url)
            # print(apikey)
            # print(product_tcin)
            parmas = {'key': apikey, 'tcin': product_tcin, 'store_id': '1157', 'store_positions_store_id': '1157',
                      'has_store_positions_store_id': 'true', 'zip': '14450', 'state': 'NY',
                      'latitude': '43.091156005859375', 'longitude': '-77.42955017089844',
                      'scheduled_delivery_store_id': '1195', 'pricing_store_id': '1157',
                      'fulfillment_test_mode': 'grocery_opu_team_member_test', 'is_bot': 'false'}
            response = requests.get("https://redsky.target.com/redsky_aggregations/v1/web/pdp_fulfillment_v1?",params=parmas)
            # print("checking if it is instock")
            # print("response: ", response)
            # print("response.headers: ", response.headers)
            print("response.text: ", i, response.text)
            if ('"order_pickup":{"availability_status":"UNAVAILABLE"' not in str(response.text)):
                instock = True
                method = "pickup"
                print("it is instock for order pickup")
            if ('"ship_to_store":{"availability_status":"UNAVAILABLE"}' not in str(response.text)):
                instock = True
                method = "shiptostore"
                print("it is instock for shipping to store")
            if ('"shipping_options":{"availability_status":"OUT_OF_STOCK"' not in str(response.text)):
                instock = True
                method = "shipping"
                print("it is instock for shipping to home")
            if instock is True:
                return url,method
def addtocart_shiptostore(req, product_url, apikey, tcin):
    headers = {'Host': 'carts.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '209',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Origin': 'https://www.target.com',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': product_url,
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {'field_groups': 'CART%2CCART_ITEMS%2CSUMMARY', 'key': apikey}
    data = {"cart_type": "REGULAR", "channel_id": "90", "shopping_context": "DIGITAL",
            "cart_item": {"tcin": tcin, "quantity": 1, "item_channel_id": "10"},
            "fulfillment": {"fulfillment_test_mode": "grocery_opu_team_member_test"}}

    response = req.post('https://carts.target.com/web_checkouts/v1/cart_items?', data=json.dumps(data), headers=headers,params=parmas)
    print("____adding to Cart for shipping to store_______")
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended adding to Cart for shipping to store_______")
    cartid = str(response.text).split("cart_id")[1].split('"')[2]
    print("cartiddd: ", cartid)
    return cartid

def addtocart_shiptohome(req, product_url, apikey, tcin):
    headers = {'Host': 'carts.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '209',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Origin': 'https://www.target.com',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': product_url,
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {'field_groups': 'CART%2CCART_ITEMS%2CSUMMARY', 'key': apikey}
    data = {"cart_type": "REGULAR", "channel_id": "90", "shopping_context": "DIGITAL",
            "cart_item": {"tcin": tcin, "quantity": 1, "item_channel_id": "10"},
            "fulfillment": {"fulfillment_test_mode": "grocery_opu_team_member_test"}}

    response = req.post('https://carts.target.com/web_checkouts/v1/cart_items?', data=json.dumps(data), headers=headers,params=parmas)
    print("____adding to Cart for shipping to home_______")
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended adding to Cart for shipping to home _______")
    cartid = str(response.text).split("cart_id")[1].split('"')[2]
    print("cartiddd: ", cartid)
    return cartid
def addtocart_pickup(req, product_url, apikey, tcin):
    headers = {'Host': 'carts.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '209',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Origin': 'https://www.target.com',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': product_url,
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {'field_groups': 'CART%2CCART_ITEMS%2CSUMMARY', 'key': apikey}
    data = {"cart_type": "REGULAR", "channel_id": "90", "shopping_context": "DIGITAL",
            "cart_item": {"tcin": tcin, "quantity": 1, "item_channel_id": "10"},
            "fulfillment": {"fulfillment_test_mode": "grocery_opu_team_member_test", "location_id": "1157",
                            "ship_method": "STORE_PICKUP"}}

    response = req.post('https://carts.target.com/web_checkouts/v1/cart_items?', data=json.dumps(data), headers=headers,params=parmas)
    print("____adding to Cart for pickup_______")
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended adding to Cart for pickup________")
    cartid = str(response.text).split("cart_id")[1].split('"')[2]
    print("cartiddd: ", cartid)
    return cartid


def request(driver):
    s = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    return s


def login():
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=C:\\Users\\nickm\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    driver = webdriver.Chrome('C:\\Users\\nickm\\Downloads\\chromedriver_win32\\chromedriver', options=options)
    driver.get('https://target.com')
    # driver.find_element_by_id('account').click()
    # driver.find_element_by_id('accountNav-signIn').click()
    # driver.find_element_by_id('username').send_keys("nickman3422@gmail.com ")
    # driver.find_element_by_id('password').send_keys("ThisisAPassword1234")
    # driver.find_element_by_id('login').click()
    # time.sleep(1000)
    # Now move to other pages using requests
    # add while and if statement with a get to desired product to check if it is in stock and if it is then send post request to add it to cart and checkout
    req = request(driver)
    return req,driver


def checkout(req, product_url, apikey, tcin,cartid):
    headers = {'Origin': 'https://www.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '23',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': 'https://www.target.com/co-review?precheckout=true',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {
        'field_groups': 'ADDRESSES,CART,CART_ITEMS,DELIVERY_WINDOWS,PAYMENT_INSTRUCTIONS,PICKUP_INSTRUCTIONS,PROMOTION_CODES,SUMMARY',
        'key': apikey}
    data = {"cart_type": "REGULAR"}
    response = req.post("https://carts.target.com/web_checkouts/v1/pre_checkout?", data=json.dumps(data),
                        headers=headers, params=parmas)
    print("____first of checkout_______")
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended first of checkout_______")
    payment_id=str(response.text).split("payment_instruction_id")[1].split('"')[2]
    print("payment_instruction_id: ",payment_id)
    headers = {'Origin': 'https://www.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '383',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': 'https://www.target.com/co-delivery',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {
        'field_groups': 'ADDRESSES,CART,CART_ITEMS,PICKUP_INSTRUCTIONS,PROMOTION_CODES,SUMMARY',
        'key': apikey}
    data = {"cart_type":"REGULAR","address":{"address_line1":"6 Tenbury Way","address_type":"SHIPPING","city":"Fairport","country":"US","first_name":"Nicholas","last_name":"Mangerian","mobile":"5852828440","save_as_default":"false","state":"NY","zip_code":"14450-8437"},"profile_address_id":"c976f480-080f-11eb-8dc8-03d4835045bd","selected":"true","save_to_profile":"false","skip_verification":"false"}
    response = req.post("https://carts.target.com/web_checkouts/v1/cart_shipping_addresses?", data=json.dumps(data),
                        headers=headers, params=parmas)
    print("____address of checkout_______")
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended address of checkout_______")
    # checkout:
    # enter card number:
    headers = {'Origin': 'https://www.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '39',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': 'https://www.target.com/co-review',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {'key': apikey}
    data = {"cart_id": cartid, "card_number": "4767718349196032"}
    response = req.post("https://carts.target.com/checkout_payments/v1/credit_card_compare?", data=json.dumps(data),
                        headers=headers, params=parmas)
    print("____card information_______")
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended card information_______")




    headers = {'Origin': 'https://www.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '122',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': 'https://www.target.com/co-review',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {'key': apikey}
    data = {"cart_id":cartid,"wallet_mode":"NONE","payment_type":"CARD","card_details":{"cvv":"363"}}
    response = req.put('https://carts.target.com/checkout_payments/v1/payment_instructions/'+payment_id+'?', data=json.dumps(data),
                        headers=headers, params=parmas)
    print("____enter CVV_______")
    print("url: ", response.url)
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended enter CVV_______")



    # place order:
    headers = {'Origin': 'https://www.target.com',
               'Connection': 'keep-alive',
               'Content-Length': '39',
               'Accept': 'application/json',
               'x-application-name': 'web',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
               'Content-Type': 'application/json',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': 'https://www.target.com/co-review',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    parmas = {'field_groups': 'ADDRESSES,CART,CART_ITEMS,DELIVERY_WINDOWS,PAYMENT_INSTRUCTIONS,PICKUP_INSTRUCTIONS,PROMOTION_CODES,SUMMARY',
        'key': apikey}
    data = {"cart_type": "REGULAR", "channel_id": 10}
    response = req.post("https://carts.target.com/web_checkouts/v1/checkout?", data=json.dumps(data), headers=headers,
                        params=parmas)
    print("____placing order_______")
    print("response: ", response)
    print("response.headers: ", response.headers)
    print("response.text: ", response.text)
    print("response.reason: ", response.reason)
    print("response.json():", response.json())
    print("____ended placing order_______")
def slowaddtochart(driver,url):
    while True:
        driver.get(url)
        element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="viewport"]/div[5]/div/div[2]/div[3]/div[1]/div/div[1]/div/div[1]/div[2]/button'))
        WebDriverWait(driver, 100).until(element_present)
        driver.find_element_by_xpath('//*[@id="viewport"]/div[5]/div/div[2]/div[3]/div[1]/div/div[1]/div/div[1]/div[2]/button').click()
def slowcheckout(driver):
    driver.get('https://www.target.com/co-cart')
    try:
        element_present = EC.presence_of_element_located((By.XPATH,'//*[@id="viewport"]/div[5]/div[2]/div[1]/div[3]/div/div[2]/div/button'))
        WebDriverWait(driver, 10).until(element_present)
        print(driver.page_source)
        print(driver.current_url)
        driver.find_element_by_xpath('//*[@id="viewport"]/div[5]/div[2]/div[1]/div[3]/div/div[2]/div/button').click()
        try:
            element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="creditCardInput-cardNumber"]'))
            WebDriverWait(driver, 2).until(element_present)
            driver.find_element_by_xpath('//*[@id="creditCardInput-cardNumber"]').send_keys("4767718349196032")
        except:
            pass
        print("didn't need to enter credit card")
        try:
            element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="STEP_PAYMENT"]/div/div[2]/div/div[1]/div/div[2]/form/div/form/div/div[2]/button'))
            WebDriverWait(driver, 1).until(element_present)
            driver.find_element_by_xpath('//*[@id="STEP_PAYMENT"]/div/div[2]/div/div[1]/div/div[2]/form/div/form/div/div[2]/button').click()
        except:
            pass
        print("didn't need to click button for credit card")
        try:
            element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="creditCardInput-cvv"]'))
            WebDriverWait(driver, 1).until(element_present)
            driver.find_element_by_xpath('//*[@id="creditCardInput-cvv"]').send_keys("636")
        except:
            pass
        print("didn't need to enter cvv")
        try:
            element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="STEP_PAYMENT"]/div/div[2]/div/div[2]/div/div/button'))
            WebDriverWait(driver, 1).until(element_present)
            driver.find_element_by_xpath('//*[@id="STEP_PAYMENT"]/div/div[2]/div/div[2]/div/div/button').click()
        except:
            pass
        print("didn't need to click button for ccv(save and continue)")
    except:
        print("nothing in cart")

# product_urls=["https://www.target.com/p/2020-nfl-mosaic-football-trading-card-blaster-box/-/A-80846428","https://www.target.com/p/2020-nfl-donruss-football-trading-card-blaster-box/-/A-80140513","https://www.target.com/p/2020-topps-mlb-bowman-baseball-trading-card-mega-box/-/A-79366642"]
#product_urls = ["https://www.target.com/p/playstation-5-console/-/A-81114595#lnk=sametab"]
#product_urls = ["https://www.target.com/p/men-s-jamarcus-oxfords-casual-dress-shoes-goodfellow-co/-/A-79605318?preselect=79482516#lnk=sametab"]
#req,driver = login()
#slowcheckout(driver)

def queue_checker_ultimente(driver):
    global inqueue
    inqueue = False
    while inqueue is False:
        driver.get('https://direct.playstation.com/en-us/consoles/console/playstation5-console.3005816')
        #print(driver.page_source)
        print(driver.current_url)
        #print(driver.current_window_handle)
        #print(driver.add_cookie())
        #print(driver.get_network_conditions())
        #print(driver.name)
        time.sleep(10)
        try:

            if("queue" in driver.current_url ):
                playsound("C:\\Users\\nickm\\Downloads\\Seinfeld.wav")
                print("it is in_______________________________________gyt9fugvbhiytutfgvhbuiytfgvyiyyrehosdin_++++++++++")
                inqueue=True
                while True:
                    time.sleep(10000)
        except:
            pass
        driver.get('https://direct.playstation.com/en-us/consoles/console/playstation5-digital-edition-console.3005817')
        # print(driver.page_source)
        print(driver.current_url)
        # print(driver.current_window_handle)
        # print(driver.add_cookie())
        # print(driver.get_network_conditions())
        # print(driver.name)
        time.sleep(10)
        try:

            if ("queue" in driver.current_url):
                playsound("C:\\Users\\nickm\\Downloads\\Seinfeld.wav")
                print(
                    "it is in_______________________________________gyt9fugvbhiytutfgvhbuiytfgvyiyyrehosdin_++++++++++")
                inqueue = True
                while True:
                    time.sleep(10000)
        except:
            pass
def refresh_page_method():
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=C:\\Users\\nickm\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome('C:\\Users\\nickm\\Downloads\\chromedriver_win32\\chromedriver', options=options)
    #driver = webdriver.Chrome('C:\\Users\\nickm\\Downloads\\chromedriver_win32\\chromedriver')
    queue_checker_ultimente(driver)
def checkallstores():
    instock = False
    while instock is False:
        response = requests.get("https://api.direct.playstation.com/commercewebservices/ps-direct-us/users/anonymous/products/productList?fields=BASIC&productCodes=3005816")
        if '"stock":{"stockLevelStatus":"outOfStock"}' not in response.text:
            print("playstation direct has disc one")
            playsound("C:\\Users\\nickm\\Downloads\\Seinfeld.wav")
            instock=True
        response = requests.get("https://api.direct.playstation.com/commercewebservices/ps-direct-us/users/anonymous/products/productList?fields=BASIC&productCodes=3005817")
        if '"stock":{"stockLevelStatus":"outOfStock"}' not in response.text:
            print("playstation direct has digital one")
            playsound("C:\\Users\\nickm\\Downloads\\Seinfeld.wav")
            instock = True
        response = requests.get("https://www.bestbuy.com/fulfillment/shipping/api/v1/fulfillment/sku;skuId=6426149;postalCode=14450;deliveryDateOption=EARLIEST_AVAILABLE_DATE")
        if '{"shippable":false' not in response.text:
            print(response.text)
            print("best buy has disc one")
            playsound("C:\\Users\\nickm\\Downloads\\Seinfeld.wav")
            instock = True
        response = requests.get("https://www.bestbuy.com/fulfillment/shipping/api/v1/fulfillment/sku;skuId=6430161;postalCode=14450;deliveryDateOption=EARLIEST_AVAILABLE_DATE")
        if '{"shippable":false' not in response.text:
            print("best buy has digital one")
            playsound("C:\\Users\\nickm\\Downloads\\Seinfeld.wav")
            instock = True


    while True:
        time.sleep(10000)



def go_to_playsation_direct():
    #options = webdriver.ChromeOptions()
    #options.add_argument("user-data-dir=C:\\Users\\nickm\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    #chrome_options.add_experimental_option("detach", True)
    #driver = webdriver.Chrome('C:\\Users\\nickm\\Downloads\\chromedriver_win32\\chromedriver', options=options)
    driver = webdriver.Chrome('C:\\Users\\nickm\\Downloads\\chromedriver_win32\\chromedriver')
    driver.get('https://direct.playstation.com')

def check_stock_method():
    instock=False
    while instock is False:
        response=requests.get("https://api.direct.playstation.com/commercewebservices/ps-direct-us/users/anonymous/products/productList?fields=BASIC&productCodes=3005816")
        print("____placing order_______")
        print( str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),"response.text: ", response.text,)

        print("____ended placing order_______")


        if '"stock":{"stockLevelStatus":"outOfStock"}' not in response.text:
            playsound("C:\\Users\\nickm\s\Downloads\\Seinfeld.wav")
            instock=True

        response = requests.get("https://api.direct.playstation.com/commercewebservices/ps-direct-us/users/anonymous/products/productList?fields=BASIC&productCodes=3005817")
        print("____placing order_______")
        print(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")), "response.text: ", response.text, )

        print("____ended placing order_______")

        if '"stock":{"stockLevelStatus":"inStock"}' in response.text:
            playsound("C:\\Users\\nickm\\Downloads\\Seinfeld.wav")
            go_to_playsation_direct()
            instock = True
        time.sleep(1)

    while True:
        time.sleep(10000)

refresh_page_method()
'''
url,method = checkifinstock(product_urls)
apikey, product_tcin = get_keys(url)
print(apikey)
print(product_tcin)
req,driver = login()
if method is "shipping":
    cartid=addtocart_shiptohome(req, url, apikey, product_tcin)
if method is "pickup":
    cartid=addtocart_pickup(req, url, apikey, product_tcin)
if method is "shiptostore":
    cartid=addtocart_shiptostore(req, url, apikey, product_tcin)
checkout(req, url, apikey, product_tcin, cartid)

time.sleep(100)
'''
