#!/usr/bin/env python3
"""
Simple MongoDB Atlas connection test
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test MongoDB Atlas connection"""
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "ecommerce_chatbot")
    
    print(f"Testing connection to: {mongodb_url}")
    print(f"Database: {database_name}")
    
    try:
        # Create client
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        print("Testing server connection...")
        client.admin.command('ping')
        print("✅ Server connection successful!")
        
        # Test database access
        print(f"Testing database access to '{database_name}'...")
        db = client[database_name]
        
        # Try to list collections
        collections = db.list_collection_names()
        print(f"✅ Database access successful! Found {len(collections)} collections: {collections}")
        
        # Try a simple write operation
        print("Testing write permissions...")
        test_collection = db.connection_test
        result = test_collection.insert_one({"test": "connection", "timestamp": "now"})
        print(f"✅ Write operation successful! Inserted document with ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup successful!")
        
        client.close()
        print("\n🎉 All tests passed! MongoDB Atlas connection is working properly.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        if "Authentication failed" in str(e):
            print("\n🔍 Authentication Issue Troubleshooting:")
            print("1. Check if username/password are correct in MongoDB Atlas")
            print("2. Verify the user has read/write permissions to the database")
            print("3. Make sure the database user is created for the correct cluster")
            print("4. Check if the password contains special characters that need URL encoding")
        
        return False

if __name__ == "__main__":
    test_connection()
