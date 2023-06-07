import streamlit as st
import pymongo
from PIL import Image
from database import add_client_to_db

def onboarding_app():
    st.title("Client Onboarding")

    name = st.text_input("Name:")
    dob = st.date_input("Date of Birth:")
    phone = st.text_input("Phone Number:")
    email = st.text_input("Email:")
    aadhar = st.text_input("Aadhar Card No:")
    pan = st.text_input("Pan Card No:")
    bank_account = st.text_input("Bank Account No:")
    profile_picture = st.file_uploader("Profile Picture", type=["png", "jpg", "jpeg"])

    st.subheader("Brokers")
    brokers = []
    add_broker = st.button("Add Broker")
    if add_broker:
        broker_name = st.selectbox("Broker Name", ["Zerodha", "AliceBlue"])
        user_name = st.text_input("User Name:")
        password = st.text_input("Password:")
        two_fa = st.text_input("2FA:")
        totp_auth = st.text_input("TotpAuth:")
        api_key = st.text_input("ApiKey:")
        api_secret = st.text_input("ApiSecret:")
        active = st.checkbox("Active:")
        capital = st.number_input("Capital:")
        risk_profile = st.text_input("Risk profile:")

        broker = {
            "broker_name": broker_name,
            "user_name": user_name,
            "password": password,
            "two_fa": two_fa,
            "totp_auth": totp_auth,
            "api_key": api_key,
            "api_secret": api_secret,
            "active": active,
            "capital": capital,
            "risk_profile": risk_profile
        }
        brokers.append(broker)

    st.subheader("Strategies Subscribed")
    strategies_subscribed = []
    add_strategy = st.button("Add Strategy")
    if add_strategy:
        strategy_name = st.text_input("Strategy Name:")
        broker = st.selectbox("Broker", [b["broker_name"] for b in brokers])
        perc_allocated = st.number_input("Percentage Allocated:")

        strategy = {
            "strategy_name": strategy_name,
            "broker": broker,
            "perc_allocated": perc_allocated
        }
        strategies_subscribed.append(strategy)

    comments = st.text_area("Comments:")

    submit = st.button("Submit")
    if submit:
        if profile_picture is not None:
            img = Image.open(profile_picture)
            img.save(f"profile_pictures/{name}.png")

        client = {
            "name": name,
            "dob": dob,
            "phone": phone,
            "email": email,
            "aadhar": aadhar,
            "pan": pan,
            "bank_account": bank_account,
            "profile_picture": f"profile_pictures/{name}.png",
            "brokers": brokers,
            "strategies_subscribed": strategies_subscribed,
            "comments": comments
        }
        add_client_to_db(client)
        st.success("Client added successfully!")

if __name__ == "__main__":
    onboarding_app()