# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time
import re, string

house_card = "/html[@class='js cssgrid ng-scope']/body[@class='secondary-background header-partially-hidden']" \
             "/main/listing-search[@class='ng-isolate-scope']/section[@class='content content--sideless-small " \
             "content--topless content--bottomless content--primary-background center-on-wallpaper']" \
             "/div[@class='content__section']/div[@class='search-result']/div[@class='sticky-side']" \
             "/search-result-cards[@class='ng-scope ng-isolate-scope']/div[@class='cards']/div[@class='cards__card ng-scope']"

def write_to_file(doc, filename):
    with open(filename, 'w') as f:
        f.write(doc)


def clean_number(str):
    str = re.sub('[^0-9, \,]', '', str.strip()).strip()
    str = str.replace(',', '.')
    return str

def clean_address(str):
    return str.strip().split('\n')[0]

if __name__ == '__main__':
    # url = 'https://asunnot.oikotie.fi/myytavat-asunnot'
    # Käpylä
    url = [['https://asunnot.oikotie.fi/myytavat-asunnot?pagination=1&locations=%5B%5B14734,5,%2200610,' \
         '%20Helsinki%22%5D%5D&cardType=100&buildingType%5B%5D=1&buildingType%5B%5D=256&constructionYear%5Bmin%5D=2010',
            "Helsinki"],
           ['https://asunnot.oikotie.fi/myytavat-asunnot?pagination=2&locations=%5B%5B14734,5,%2200610,' \
           '%20Helsinki%22%5D%5D&cardType=100&buildingType%5B%5D=1&buildingType%5B%5D=256&constructionYear%5Bmin%5D=2010',
           "Helsinki"],
           ['https://asunnot.oikotie.fi/myytavat-asunnot?pagination=3&locations=%5B%5B14734,5,%2200610,' \
           '%20Helsinki%22%5D%5D&cardType=100&buildingType%5B%5D=1&buildingType%5B%5D=256&constructionYear%5Bmin%5D=2010',
            "Helsinki"]]
    # Valkeakoski
    url += [['https://asunnot.oikotie.fi/myytavat-uudisasunnot?pagination=1&habitationType%5B%5D=1&locations=%5B%5B76,'
           '6,%22Hämeenlinna%22%5D%5D&buildingType%5B%5D=1&buildingType%5B%5D=256&constructionYear%5Bmin%5D=2018&cardType=200',
             "Valkeakoski"],
            ['https://asunnot.oikotie.fi/myytavat-uudisasunnot?pagination=2&habitationType%5B%5D=1&locations=%5B%5B76,'
           '6,%22Hämeenlinna%22%5D%5D&buildingType%5B%5D=1&buildingType%5B%5D=256&constructionYear%5Bmin%5D=2018&cardType=200',
             "Valkeakoski"],
            ['https://asunnot.oikotie.fi/myytavat-uudisasunnot?pagination=3&habitationType%5B%5D=1&locations=%5B%5B76,'
           '6,%22Hämeenlinna%22%5D%5D&buildingType%5B%5D=1&buildingType%5B%5D=256&constructionYear%5Bmin%5D=2018&cardType=200',
             "Valkeakoski"]
            ]

    driver = webdriver.Safari()
    data = []
    for ind, u in enumerate(url):
        driver.get(u[0])
        try:
            WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[src^='https://cdn.privacy-mgmt.com/index']")))
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='OK']"))).click()
            driver.switch_to.default_content()
        except:
            pass
        time.sleep(2) # TODO: should be replaced with WebDriverWait.until

        prices = driver.find_elements_by_class_name("ot-card__price")
        areas = driver.find_elements_by_class_name("ot-card__size")
        addresses = driver.find_elements_by_class_name("ot-card__address")

        assert len(prices) == len(areas)
        assert len(prices) == len(addresses)
        for address, price, area in zip(addresses, prices, areas):
            p = clean_number(price.text)
            a = clean_number(area.text)
            add = clean_address(address.text)
            price_area = float(p) / float(a)
            data.append([u[1], add, p, a, str(price_area)])
            # print(add, p, a, price_area)
            # cards = driver.find_element_by_xpath(house_card)
    with open('asunnot.csv', 'w') as f:
        # header
        f.write('city, address, price, size, price_per_area\n')
        for d in data:
            f.write(','.join(d) + '\n')

    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # write_to_file(soup.prettify(), 'asunnot.html')
    # print(soup)
