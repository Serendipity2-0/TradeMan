import os
import pymongo
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyotp import TOTP
import time
import requests
import json

load_dotenv()

# Connect to MongoDB
client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = client["UserProfiles"]
collection = db["clients"]

def get_active_brokers():
    active_brokers = []
    for user in collection.find({"brokers.Active": True}):
        active_brokers.extend(user["brokers"])
    return active_brokers

def loginKite(username, password, totp_key, api_key, api_secret):
    driver = webdriver.Chrome()
    driver.get("https://kite.zerodha.com/")

    # Login
    driver.find_element_by_xpath('//*[@id="userid"]').send_keys(username)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
    driver.find_element_by_xpath('//*[@type="submit"]').click()
    time.sleep(2)

    # 2FA
    driver.find_element_by_xpath('//*[@id="pin"]').send_keys(TOTP(totp_key).now())
    driver.find_element_by_xpath('//*[@type="submit"]').click()
    time.sleep(2)

    # Get access token
    request_token = driver.current_url.split("request_token=")[1].split("&action=")[0]
    driver.quit()

    # Get access token using API
    data = {
        "api_key": api_key,
        "api_secret": api_secret,
        "request_token": request_token
    }
    response = requests.post("https://api.kite.trade/session/token", data=data)
    access_token = json.loads(response.text)["access_token"]

    return access_token

def loginAnt(username, password, totp_key, api_key, api_secret):
    # Implement login function for AliceBlue
    pass

def update_brokers_env(active_brokers):
    for broker in active_brokers:
        if broker["BrokerName"] == "Zerodha":
            access_token = loginKite(broker["UserName"], broker["Password"], broker["TotpAuth"], broker["ApiKey"], broker["ApiSecret"])
            os.environ[f"kite_access_tkn_{broker['UserName']}"] = access_token
        elif broker["BrokerName"] == "AliceBlue":
            access_token = loginAnt(broker["UserName"], broker["Password"], broker["TotpAuth"], broker["ApiKey"], broker["ApiSecret"])
            os.environ[f"ant_access_tkn_{broker['UserName']}"] = access_token

def getCurrentCapital(broker):
    # Implement function to get current capital for each broker
    pass

def send_daily_telegram_reports(active_brokers):
    for broker in active_brokers:
        current_capital = getCurrentCapital(broker)
        for strategy in broker["Strategies_subscribed"]:
            cap_allocated = current_capital * strategy["Perc_Allocated"]
            os.environ[f"{broker['BrokerName']}_{strategy['StrategyName']}_cap_{broker['UserName']}"] = str(cap_allocated)

            # Send telegram message
            # Implement function to send telegram message to individual trading group using group id in telegram
            pass

if __name__ == "__main__":
    active_brokers = get_active_brokers()
    update_brokers_env(active_brokers)
    send_daily_telegram_reports(active_brokers)