#!/usr/bin/env python3
"""
Setup script to create data directory and run CSV parser
"""
import os
import sys
from csv_parser import CSVParser

def create_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created {data_dir} directory")
        print(f"Please place your CSV files in the {data_dir} directory:")
        print("- distribution_centers.csv")
        print("- inventory_items.csv")
        print("- order_items.csv")
        print("- orders.csv")
        print("- products.csv")
        print("- users.csv")
        return False
    return True

def check_csv_files():
    """Check if all required CSV files exist"""
    required_files = [
        "distribution_centers.csv",
        "inventory_items.csv", 
        "order_items.csv",
        "orders.csv",
        "products.csv",
        "users.csv"
    ]
    
    data_dir = "data"
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print("Missing CSV files:")
        for file in missing_files:
            print(f"- {file}")
        return False
    
    return True

def main():
    print("Setting up e-commerce chatbot data...")
    
    # Create data directory
    if not create_data_directory():
        return
    
    # Check for CSV files
    if not check_csv_files():
        print("\nPlease add the missing CSV files to the data directory and run this script again.")
        return
    
    # Parse and load data
    print("All CSV files found. Loading data into MongoDB...")
    parser = CSVParser()
    parser.load_all_data()
    print("Data setup completed successfully!")

if __name__ == "__main__":
    main()
