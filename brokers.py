import os
from dotenv import load_dotenv, set_key
from kiteconnect import KiteConnect
from alice_blue import AliceBlue

load_dotenv("brokers.env")

def loginKite(username):
    api_key = os.getenv(f"kite_api_key_{username}")
    api_secret = os.getenv(f"kite_api_sec_{username}")
    kite_username = os.getenv(f"kite_username_{username}")
    kite_password = os.getenv(f"kite_password_{username}")
    kite_totp_key = os.getenv(f"kite_totp_key_{username}")

    kite = KiteConnect(api_key=api_key)
    request_token = kite.generate_session(kite_username, api_secret)
    access_token = request_token["access_token"]
    set_key("brokers.env", f"kite_access_tkn_{username}", access_token)

    return kite

def loginAnt(username):
    api_key = os.getenv(f"ant_api_key_{username}")
    api_secret = os.getenv(f"ant_api_sec_{username}")
    ant_username = os.getenv(f"ant_username_{username}")
    ant_password = os.getenv(f"ant_password_{username}")
    ant_totp_key = os.getenv(f"ant_totp_key_{username}")

    alice = AliceBlue(username=ant_username, password=ant_password, access_token=api_key, master_contracts_to_download=['NSE'])
    access_token = alice.get_access_token()
    set_key("brokers.env", f"ant_access_tkn_{username}", access_token)

    return alice