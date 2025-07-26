import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Direct MongoDB Atlas connection
MONGODB_URL = "mongodb+srv://godnanijatin:Vj7ZIuzkl5wX0aiY@cluster0.l0mhrl9.mongodb.net/ecommerce_chatbot?retryWrites=true&w=majority"
DATABASE_NAME = "ecommerce_chatbot"

class Database:
    client: AsyncIOMotorClient = None
    database = None

# Async database instance for FastAPI
db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(MONGODB_URL)
    db.database = db.client[DATABASE_NAME]
    print(f"Connected to MongoDB at {MONGODB_URL}")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database

# Sync client for data population scripts
def get_sync_database():
    """Get synchronous database connection for data population"""
    client = MongoClient(MONGODB_URL)
    return client[DATABASE_NAME]
