import streamlit as st
import pymongo
from pymongo import MongoClient
import os

# Connect to MongoDB
MONGO_URL = os.environ.get("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["UserProfiles"]
clients_collection = db["clients"]

def create_user(email, password):
    user = clients_collection.find_one({"email": email})
    if user:
        return False
    else:
        clients_collection.insert_one({"email": email, "password": password})
        return True

def login_user(email, password):
    user = clients_collection.find_one({"email": email, "password": password})
    return user

def save_user_profile(user_data):
    clients_collection.update_one({"email": user_data["email"]}, {"$set": user_data})

def main():
    st.title("Serendipity Trading Firm")
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.success("Logged in as {}".format(email))
                user_data = clients_collection.find_one({"email": email})
                st.write(user_data)
            else:
                st.warning("Incorrect email or password")

    elif choice == "Register":
        st.subheader("Register")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            if create_user(email, password):
                st.success("Account created for {}".format(email))
                st.info("Go to Login")
            else:
                st.warning("Email already exists")

if __name__ == "__main__":
    main()