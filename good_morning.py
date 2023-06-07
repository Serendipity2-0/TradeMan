import os
from dotenv import load_dotenv, set_key
from pymongo import MongoClient
from brokers import loginKite, loginAnt
from telegram_bot import send_telegram_message
from database import get_active_brokers, get_current_capital

def update_access_token(broker_details):
    for broker in broker_details:
        if broker["broker_name"] == "Zerodha":
            access_token = loginKite(broker["api_key"], broker["api_secret"], broker["user_name"], broker["password"], broker["totp_auth"])
        elif broker["broker_name"] == "AliceBlue":
            access_token = loginAnt(broker["api_key"], broker["api_secret"], broker["user_name"], broker["password"], broker["totp_auth"])
        
        env_var_name = f'{broker["broker_name"]}_access_tkn_{broker["user_name"]}'
        set_key(".env", env_var_name, access_token)

def send_daily_reports(active_brokers):
    for broker in active_brokers:
        current_capital = get_current_capital(broker["broker_name"], broker["api_key"], broker["api_secret"], broker["access_token"])
        for strategy in broker["strategies_subscribed"]:
            allocated_capital = current_capital * (strategy["perc_allocated"] / 100)
            env_var_name = f'{broker["broker_name"]}_{strategy["strategy_name"]}_cap_{broker["user_name"]}'
            set_key(".env", env_var_name, str(allocated_capital))
            message = f'Daily Report: {broker["broker_name"]} - {strategy["strategy_name"]} - Capital: {allocated_capital}'
            send_telegram_message(broker["telegram_group_id"], message)

def main():
    load_dotenv()
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["UserProfiles"]
    
    active_brokers = get_active_brokers(db)
    update_access_token(active_brokers)
    send_daily_reports(active_brokers)

if __name__ == "__main__":
    main()