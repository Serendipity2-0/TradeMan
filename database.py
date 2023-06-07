import pymongo
from pymongo import MongoClient

def connect_to_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["UserProfiles"]
    return db

def add_client_to_db(client_data):
    db = connect_to_db()
    clients_collection = db["clients"]
    clients_collection.insert_one(client_data)

def get_active_brokers():
    db = connect_to_db()
    clients_collection = db["clients"]
    active_brokers = []
    for client in clients_collection.find():
        for broker in client["brokers"]:
            if broker["active"]:
                active_brokers.append(broker)
    return active_brokers