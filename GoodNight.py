import os
import pandas as pd
import sqlite3
from telegram import Bot

# Your telegram bot token and channel ID
BOT_TOKEN = 'YOUR_BOT_TOKEN'
CHANNEL_ID = 'YOUR_CHANNEL_ID'

# Will be used in the future
def calculate_nse_taxes(trade_type: str, total_value: float) -> float:
    brokerage = 0
    stt_ctt = 0
    transaction_charges = 0
    gst = 0
    sebi_charges = 0
    stamp_charges = 0
    
    if trade_type == "equity_delivery":
        brokerage = 0
        stt_ctt = 0.001 * total_value  # 0.1% on buy & sell
        transaction_charges = max(0.00325, 0.00375) * total_value  # NSE: 0.00325%, BSE: 0.00375%
        gst = 0.18 * (brokerage + sebi_charges + transaction_charges)  # 18% on (brokerage + SEBI charges + transaction charges)
        sebi_charges = (10 / 100000000) * total_value + gst  # ₹10 / crore + GST
        stamp_charges = 0.00015 * total_value  # 0.015% or ₹1500 / crore on buy side

    elif trade_type == "equity_intraday":
        brokerage = min(20, 0.0003 * total_value)  # 0.03% or Rs. 20/executed order whichever is lower
        stt_ctt = 0.00025 * total_value  # 0.025% on the sell side
        transaction_charges = max(0.00325, 0.00375) * total_value  # NSE: 0.00325%, BSE: 0.00375%
        gst = 0.18 * (brokerage + sebi_charges + transaction_charges)  # 18% on (brokerage + SEBI charges + transaction charges)
        sebi_charges = (10 / 100000000) * total_value + gst  # ₹10 / crore + GST
        stamp_charges = 0.00003 * total_value  # 0.003% or ₹300 / crore on buy side

    elif trade_type == "F&O_futures":
        brokerage = min(20, 0.0003 * total_value)  # 0.03% or Rs. 20/executed order whichever is lower
        stt_ctt = 0.000125 * total_value  # 0.0125% on the sell side
        transaction_charges = 0.0019 * total_value  # NSE: 0.0019%
        gst = 0.18 * (brokerage + sebi_charges + transaction_charges)  # 18% on (brokerage + SEBI charges + transaction charges)
        sebi_charges = (10 / 100000000) * total_value + gst  # ₹10 / crore + GST
        stamp_charges = 0.00002 * total_value  # 0.002% or ₹200 / crore on buy side

    elif trade_type == "F&O_options":
        brokerage = 20  # Flat Rs. 20 per executed order
        stt_ctt = max(0.00125 * total_value, 0.000625 * total_value) # 0.125% of the intrinsic value on options that are bought and exercised 0.0625% on sell side (on premium)
        transaction_charges = max(0.05, 0.005) * total_value  # NSE: 0.05% (on premium), BSE: 0.005% (on premium)
        gst = 0.18 * (brokerage + sebi_charges + transaction_charges)  # 18% on (brokerage + SEBI charges + transaction charges)
        sebi_charges = (10 / 100000000) * total_value + gst  # ₹10 / crore + GST
        stamp_charges = 0.00003 * total_value  # 0.003% or ₹300 / crore on buy side

    else:
        raise ValueError("Invalid trade type")

    total_taxes = brokerage + stt_ctt + transaction_charges + gst + sebi_charges + stamp_charges
    return total_taxes

def calculate_taxes(total_value: float) -> float:
    brokerage = 20  # Flat Rs. 20 per executed order
    stt_ctt = 0.00125 * total_value  # 0.125% on premium
    transaction_charges = 0.05 * total_value  # NSE: 0.05% (on premium)
    sebi_charges = (10 / 100000000) * total_value  # ₹10 / crore
    gst = 0.18 * (brokerage + sebi_charges + transaction_charges)  # 18% on (brokerage + SEBI charges + transaction charges)
    stamp_charges = 0.00003 * total_value  # 0.003% or ₹300 / crore on buy side

    total_taxes = brokerage + stt_ctt + transaction_charges + gst + sebi_charges + stamp_charges
    return total_taxes


def send_telegram_message(bot_token, channel_id, message):
    bot = Bot(token=bot_token)
    bot.send_message(chat_id=channel_id, text=message)

def process_files():
    conn = sqlite3.connect('trades.db')
    bot = Bot(token=BOT_TOKEN)

    for filename in os.listdir('.'):
        if filename.endswith('.csv'):
            df = pd.read_csv(filename)
            
            # check if it's a signal file or an account file
            if '_Signal' in filename:
                table_name = 'signal'
            else:
                table_name = 'account'
                df['Taxes'] = df['Gross PnL'].apply(calculate_taxes)
                df['NetPnL'] = df['Gross PnL'] - df['Taxes']

            # save to SQLite
            df.to_sql(table_name, conn, if_exists='append', index=False)

            # send EOD report to telegram if it's the last date in the file
            if df['Date'].max() == pd.to_datetime('today').date():
                gross_pnl = df['Gross PnL'].sum()
                message = f"EOD Report for {df['Date'].max().strftime('%d%b%y')}\n\nGrossPnL : ₹{gross_pnl:,.2f}"
                send_telegram_message(BOT_TOKEN, CHANNEL_ID, message)

if __name__ == "__main__":
    process_files()
