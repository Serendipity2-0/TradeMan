import os
import requests
from dotenv import load_dotenv
from good_morning import get_active_brokers, get_current_capital

load_dotenv("brokers.env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_GROUP_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response.json()

def generate_daily_report():
    active_brokers = get_active_brokers()
    current_capital = get_current_capital(active_brokers)
    report = "Daily Capital Report:\n\n"

    for broker in active_brokers:
        user_name = broker["user_name"]
        broker_name = broker["broker_name"]
        strategies = broker["strategies_subscribed"]

        for strategy in strategies:
            strategy_name = strategy["strategy_name"]
            perc_allocated = strategy["perc_allocated"]
            capital_key = f"{broker_name}_{strategy_name}_cap_{user_name}"
            capital = current_capital[capital_key]
            allocated_capital = capital * perc_allocated / 100
            report += f"{broker_name} - {user_name} - {strategy_name}: {allocated_capital:.2f}\n"

    return report

def send_daily_report():
    report = generate_daily_report()
    send_telegram_message(report)

if __name__ == "__main__":
    send_daily_report()