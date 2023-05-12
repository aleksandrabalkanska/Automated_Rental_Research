from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import time
import auth

GOOGLE_FORM = auth.GOOGLE_FORM
ZILLOW_URL = "https://www.zillow.com/san-francisco-ca/rentals/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22north%22%3A37.902996184295844%2C%22east%22%3A-122.25136844042969%2C%22south%22%3A37.64736675330429%2C%22west%22%3A-122.61529055957031%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A20330%2C%22regionType%22%3A6%7D%5D%2C%22mapZoom%22%3A11%7D"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Accept-Language": "en-US,en;q=0.5",
}

# Driver Set Up
chrome_driver_path = r"C:\Users\Aleks\PycharmProjects\pythonProject\chromedriver_win32\chromedriver.exe"
service = Service(executable_path=chrome_driver_path)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Scrape Zillow
response = requests.get(url=ZILLOW_URL, headers=headers)
zillow_search = response.text
soup = BeautifulSoup(zillow_search, "html.parser")


all_links = [link.get("href") for link in soup.find_all(name="a", class_="property-card-link")]
all_addresses = soup.find_all(name="address")
all_prices = soup.find_all("span", attrs={"data-test": "property-card-price"})

new_links = []
new_addresses = []
new_prices = []

for link in all_links:
    if "https" not in link:
        new_links.append(f"https://www.zillow.com{link}")
    else:
        new_links.append(link)


for address in all_addresses:
    new_address = address.getText()
    if "|" in new_address:
        new_address = new_address.split("|")[1].strip()
    new_addresses.append(new_address)


for price in all_prices:
    new_price = price.getText()
    if "/" in price:
        new_price = new_price.split("/")[0].strip("/mo")
    else:
        new_price = new_price.split("+")[0].strip("/mo")
    new_prices.append(new_price)


keys = ["Address", "Price", "Link"]

listings = [{key: value for key, value in zip(keys, info)} for info in zip(new_addresses, new_prices, new_links)]

driver.get(GOOGLE_FORM)
for entry in range(0, len(listings)):
    address_field = driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="i1"]')
    time.sleep(2)
    address_field.send_keys(listings[entry]["Address"])
    price_field = driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="i5"]')
    price_field.send_keys(listings[entry]["Price"])
    link_field = driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="i9"]')
    link_field.send_keys(listings[entry]["Link"])

    submit_button = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div')
    submit_button.click()
    time.sleep(2)
    submit_again = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a')
    submit_again.click()
driver.quit()
