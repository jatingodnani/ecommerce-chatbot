#!/usr/bin/env python3
"""
Direct data loader using the same connection method as FastAPI server
"""
import pandas as pd
import os
from datetime import datetime
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the exact same connection string as the working FastAPI server
MONGODB_URL = "mongodb+srv://godnanijatin:HN0COBIxMHvSE2gG@cluster0.l0mhrl9.mongodb.net/ecommerce_chatbot?retryWrites=true&w=majority"
DATABASE_NAME = "ecommerce_chatbot"

class DirectDataLoader:
    def __init__(self, csv_directory="data"):
        self.csv_directory = csv_directory
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB using the same method as FastAPI"""
        try:
            logger.info(f"Connecting to MongoDB at {MONGODB_URL}")
            self.client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=30000)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful!")
            
            self.db = self.client[DATABASE_NAME]
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
    
    def disconnect(self):
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

    def load_distribution_centers(self):
        """Load distribution centers from CSV"""
        file_path = os.path.join(self.csv_directory, "distribution_centers.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        logger.info("Loading distribution centers...")
        df = pd.read_csv(file_path)
        collection = self.db.distribution_centers
        
        # Clear existing data
        result = collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} existing distribution centers")
        
        documents = []
        for _, row in df.iterrows():
            doc = {
                "center_id": int(row['id']),
                "name": str(row['name']),
                "latitude": float(row['latitude']),
                "longitude": float(row['longitude'])
            }
            documents.append(doc)
        
        if documents:
            result = collection.insert_many(documents)
            logger.info(f"✅ Inserted {len(result.inserted_ids)} distribution centers")
            return True
        return False

    def load_products(self):
        """Load products from CSV"""
        file_path = os.path.join(self.csv_directory, "products.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        logger.info("Loading products...")
        df = pd.read_csv(file_path)
        collection = self.db.products
        
        # Clear existing data
        result = collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} existing products")
        
        # Process in batches to avoid memory issues
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            documents = []
            
            for _, row in batch_df.iterrows():
                doc = {
                    "product_id": int(row['id']),
                    "cost": float(row['cost']),
                    "category": str(row['category']),
                    "name": str(row['name']),
                    "brand": str(row['brand']),
                    "retail_price": float(row['retail_price']),
                    "department": str(row['department']),
                    "sku": str(row['sku']),
                    "distribution_center_id": int(row['distribution_center_id'])
                }
                documents.append(doc)
            
            if documents:
                result = collection.insert_many(documents)
                total_inserted += len(result.inserted_ids)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} products")
        
        logger.info(f"✅ Total products inserted: {total_inserted}")
        return True

    def load_users(self):
        """Load users from CSV"""
        file_path = os.path.join(self.csv_directory, "users.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        logger.info("Loading users...")
        df = pd.read_csv(file_path)
        collection = self.db.users
        
        # Clear existing data
        result = collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} existing users")
        
        # Process in batches
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            documents = []
            
            for _, row in batch_df.iterrows():
                created_at = self.parse_datetime(row['created_at'])
                if created_at is None:
                    created_at = datetime.utcnow()
                    
                doc = {
                    "user_id": int(row['id']),
                    "first_name": str(row['first_name']),
                    "last_name": str(row['last_name']),
                    "email": str(row['email']),
                    "age": int(row['age']),
                    "gender": str(row['gender']),
                    "state": str(row['state']),
                    "street_address": str(row['street_address']),
                    "postal_code": str(row['postal_code']),
                    "city": str(row['city']),
                    "country": str(row['country']),
                    "latitude": float(row['latitude']),
                    "longitude": float(row['longitude']),
                    "traffic_source": str(row['traffic_source']),
                    "created_at": created_at
                }
                documents.append(doc)
            
            if documents:
                result = collection.insert_many(documents)
                total_inserted += len(result.inserted_ids)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} users")
        
        logger.info(f"✅ Total users inserted: {total_inserted}")
        return True

    def load_orders(self):
        """Load orders from CSV"""
        file_path = os.path.join(self.csv_directory, "orders.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        logger.info("Loading orders...")
        df = pd.read_csv(file_path)
        collection = self.db.orders
        
        # Clear existing data
        result = collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} existing orders")
        
        # Process in batches
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            documents = []
            
            for _, row in batch_df.iterrows():
                doc = {
                    "order_id": int(row['order_id']),
                    "user_id": int(row['user_id']),
                    "status": str(row['status']),
                    "gender": str(row['gender']),
                    "created_at": self.parse_datetime(row['created_at']) or datetime.utcnow(),
                    "returned_at": self.parse_datetime(row['returned_at']),
                    "shipped_at": self.parse_datetime(row['shipped_at']),
                    "delivered_at": self.parse_datetime(row['delivered_at']),
                    "num_of_item": int(row['num_of_item'])
                }
                documents.append(doc)
            
            if documents:
                result = collection.insert_many(documents)
                total_inserted += len(result.inserted_ids)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} orders")
        
        logger.info(f"✅ Total orders inserted: {total_inserted}")
        return True

    def load_inventory_items(self):
        """Load inventory items from CSV - this is the largest file"""
        file_path = os.path.join(self.csv_directory, "inventory_items.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        logger.info("Loading inventory items (this may take a while for large files)...")
        
        # Read in chunks to handle large files
        chunk_size = 5000
        collection = self.db.inventory_items
        
        # Clear existing data
        result = collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} existing inventory items")
        
        total_inserted = 0
        chunk_num = 0
        
        for chunk_df in pd.read_csv(file_path, chunksize=chunk_size):
            chunk_num += 1
            documents = []
            
            for _, row in chunk_df.iterrows():
                doc = {
                    "inventory_id": int(row['id']),
                    "product_id": int(row['product_id']),
                    "created_at": self.parse_datetime(row['created_at']) or datetime.utcnow(),
                    "sold_at": self.parse_datetime(row['sold_at']),
                    "cost": float(row['cost']),
                    "product_category": str(row['product_category']),
                    "product_name": str(row['product_name']),
                    "product_brand": str(row['product_brand']),
                    "product_retail_price": float(row['product_retail_price']),
                    "product_department": str(row['product_department']),
                    "product_sku": str(row['product_sku']),
                    "product_distribution_center_id": int(row['product_distribution_center_id'])
                }
                documents.append(doc)
            
            if documents:
                result = collection.insert_many(documents)
                total_inserted += len(result.inserted_ids)
                logger.info(f"Inserted chunk {chunk_num}: {len(result.inserted_ids)} inventory items (Total: {total_inserted})")
        
        logger.info(f"✅ Total inventory items inserted: {total_inserted}")
        return True

    def load_order_items(self):
        """Load order items from CSV"""
        file_path = os.path.join(self.csv_directory, "order_items.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        logger.info("Loading order items...")
        
        # Read in chunks
        chunk_size = 5000
        collection = self.db.order_items
        
        # Clear existing data
        result = collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} existing order items")
        
        total_inserted = 0
        chunk_num = 0
        
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
                result = collection.insert_many(documents)
                total_inserted += len(result.inserted_ids)
                logger.info(f"Inserted chunk {chunk_num}: {len(result.inserted_ids)} order items (Total: {total_inserted})")
        
        logger.info(f"✅ Total order items inserted: {total_inserted}")
        return True

    def load_all_data(self):
        """Load all CSV data into MongoDB"""
        logger.info("🚀 Starting data loading process...")
        
        if not self.connect():
            logger.error("❌ Failed to connect to MongoDB. Aborting data load.")
            return False
        
        try:
            success = True
            success &= self.load_distribution_centers()
            success &= self.load_products()
            success &= self.load_users()
            success &= self.load_orders()
            success &= self.load_inventory_items()
            success &= self.load_order_items()
            
            if success:
                logger.info("🎉 All data loaded successfully!")
            else:
                logger.error("❌ Some data loading operations failed")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Error during data loading: {e}")
            return False
        finally:
            self.disconnect()

def main():
    loader = DirectDataLoader()
    success = loader.load_all_data()
    
    if success:
        print("\n✅ Data loading completed successfully!")
        print("You can now start using your chatbot with the loaded data.")
    else:
        print("\n❌ Data loading failed. Please check the logs above.")

if __name__ == "__main__":
    main()
