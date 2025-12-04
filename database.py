from pymongo import MongoClient

client = MongoClient("mongodb+srv://kompetchn_db_user:HGBrOKNFO22mx9lQ@cluster0.tachvl5.mongodb.net/?appName=Cluster0")

db = client["order_management"]            # Database
orders_collection = db["orders"]           # Collection
