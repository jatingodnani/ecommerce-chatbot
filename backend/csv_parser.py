import pandas as pd
import os
from datetime import datetime
from database import get_sync_database
from models import (
    DistributionCenter, Product, User, Order, 
    InventoryItem, OrderItem
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVParser:
    def __init__(self, csv_directory="data"):
        self.csv_directory = csv_directory
        self.db = get_sync_database()
        
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
            return
            
        df = pd.read_csv(file_path)
        collection = self.db.distribution_centers
        
        # Clear existing data
        collection.delete_many({})
        
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
            collection.insert_many(documents)
            logger.info(f"Inserted {len(documents)} distribution centers")

    def load_products(self):
        """Load products from CSV"""
        file_path = os.path.join(self.csv_directory, "products.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return
            
        df = pd.read_csv(file_path)
        collection = self.db.products
        
        # Clear existing data
        collection.delete_many({})
        
        documents = []
        for _, row in df.iterrows():
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
            collection.insert_many(documents)
            logger.info(f"Inserted {len(documents)} products")

    def load_users(self):
        """Load users from CSV"""
        file_path = os.path.join(self.csv_directory, "users.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return
            
        df = pd.read_csv(file_path)
        collection = self.db.users
        
        # Clear existing data
        collection.delete_many({})
        
        documents = []
        for _, row in df.iterrows():
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
            collection.insert_many(documents)
            logger.info(f"Inserted {len(documents)} users")

    def load_orders(self):
        """Load orders from CSV"""
        file_path = os.path.join(self.csv_directory, "orders.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return
            
        df = pd.read_csv(file_path)
        collection = self.db.orders
        
        # Clear existing data
        collection.delete_many({})
        
        documents = []
        for _, row in df.iterrows():
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
            collection.insert_many(documents)
            logger.info(f"Inserted {len(documents)} orders")

    def load_inventory_items(self):
        """Load inventory items from CSV"""
        file_path = os.path.join(self.csv_directory, "inventory_items.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return
            
        df = pd.read_csv(file_path)
        collection = self.db.inventory_items
        
        # Clear existing data
        collection.delete_many({})
        
        documents = []
        for _, row in df.iterrows():
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
            collection.insert_many(documents)
            logger.info(f"Inserted {len(documents)} inventory items")

    def load_order_items(self):
        """Load order items from CSV"""
        file_path = os.path.join(self.csv_directory, "order_items.csv")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return
            
        df = pd.read_csv(file_path)
        collection = self.db.order_items
        
        # Clear existing data
        collection.delete_many({})
        
        documents = []
        for _, row in df.iterrows():
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
            collection.insert_many(documents)
            logger.info(f"Inserted {len(documents)} order items")

    def load_all_data(self):
        """Load all CSV data into MongoDB"""
        logger.info("Starting data loading process...")
        
        self.load_distribution_centers()
        self.load_products()
        self.load_users()
        self.load_orders()
        self.load_inventory_items()
        self.load_order_items()
        
        logger.info("Data loading completed!")

if __name__ == "__main__":
    parser = CSVParser()
    parser.load_all_data()
