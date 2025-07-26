#!/usr/bin/env python3
"""
Load only order_items CSV data without touching existing collections
"""
import pandas as pd
import os
from datetime import datetime
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the same connection string as the working FastAPI server
MONGODB_URL = "mongodb+srv://godnanijatin:Vj7ZIuzkl5wX0aiY@cluster0.l0mhrl9.mongodb.net/ecommerce_chatbot?retryWrites=true&w=majority"
DATABASE_NAME = "ecommerce_chatbot"

class OrderItemsLoader:
    def __init__(self, csv_directory="data"):
        self.csv_directory = csv_directory
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB using async Motor client"""
        try:
            logger.info(f"Connecting to MongoDB at {MONGODB_URL}")
            self.client = AsyncIOMotorClient(MONGODB_URL)
            self.db = self.client[DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def parse_datetime(self, date_str):
        """Parse datetime string, handle empty values"""
        if pd.isna(date_str) or date_str == '':
            return None
        try:
            return datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
        except:
            try:
                return datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
            except:
                return None

    async def load_order_items_only(self):
        """Load ONLY order items from CSV without touching other collections"""
        file_path = os.path.join(self.csv_directory, "order_items.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        logger.info("Loading order items only (preserving all other data)...")
        
        collection = self.db.order_items
        
        # Check current count
        current_count = await collection.count_documents({})
        logger.info(f"Current order_items count: {current_count}")
        
        if current_count > 0:
            logger.info("Order items already exist. Clearing only order_items collection...")
            result = await collection.delete_many({})
            logger.info(f"Cleared {result.deleted_count} existing order items")
        
        # Read in chunks to handle large files efficiently
        chunk_size = 3000
        total_inserted = 0
        chunk_num = 0
        
        logger.info("Starting order items data loading...")
        
        for chunk_df in pd.read_csv(file_path, chunksize=chunk_size):
            chunk_num += 1
            documents = []
            
            for _, row in chunk_df.iterrows():
                doc = {
                    "item_id": int(row['id']),
                    "order_id": int(row['order_id']),
                    "user_id": int(row['user_id']),
                    "product_id": int(row['product_id']),
                    "inventory_item_id": int(row['inventory_item_id']),
                    "status": str(row['status']),
                    "created_at": self.parse_datetime(row['created_at']) or datetime.utcnow(),
                    "shipped_at": self.parse_datetime(row['shipped_at']),
                    "delivered_at": self.parse_datetime(row['delivered_at']),
                    "returned_at": self.parse_datetime(row['returned_at'])
                }
                documents.append(doc)
            
            if documents:
                result = await collection.insert_many(documents)
                total_inserted += len(result.inserted_ids)
                logger.info(f"✅ Inserted chunk {chunk_num}: {len(result.inserted_ids)} order items (Total: {total_inserted})")
        
        logger.info(f"🎉 Order items loading completed! Total inserted: {total_inserted}")
        return True

    async def verify_data_integrity(self):
        """Verify all collections have data and show final stats"""
        logger.info("Verifying data integrity...")
        
        collections = [
            "distribution_centers", "products", "users", 
            "orders", "inventory_items", "order_items"
        ]
        
        stats = {}
        for collection_name in collections:
            collection = self.db[collection_name]
            count = await collection.count_documents({})
            stats[collection_name] = count
            logger.info(f"✅ {collection_name}: {count:,} documents")
        
        return stats

async def main():
    loader = OrderItemsLoader()
    
    if not await loader.connect():
        logger.error("❌ Failed to connect to MongoDB. Aborting.")
        return False
    
    try:
        # Load only order items
        success = await loader.load_order_items_only()
        
        if success:
            # Verify all data
            stats = await loader.verify_data_integrity()
            
            print("\n🎉 Order items loading completed successfully!")
            print("\n📊 Final Database Statistics:")
            for collection, count in stats.items():
                print(f"  • {collection}: {count:,} documents")
            
            print("\n✅ Your e-commerce chatbot database is now complete!")
            print("You can now use the chatbot with full order tracking capabilities.")
        else:
            print("\n❌ Order items loading failed.")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Error during order items loading: {e}")
        return False
    finally:
        await loader.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
