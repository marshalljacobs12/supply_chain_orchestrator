#!/usr/bin/env python3
# scripts/drop_products_table.py

from sqlalchemy import create_engine, MetaData, Table, inspect
import os

# Database connection 
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/supply_chain_db")
engine = create_engine(DB_URL)
metadata = MetaData()

def drop_products_table():
    """Drop the products table if it exists."""
    try:
        # Check if products table exists
        inspector = inspect(engine)
        if "products" in inspector.get_table_names():
            # Use raw SQL for dropping the table with CASCADE option
            print("Products table exists. Dropping table...")
            with engine.connect() as connection:
                connection.execute("DROP TABLE IF EXISTS products CASCADE")
                connection.execute("COMMIT")
            print("Products table has been successfully dropped.")
        else:
            print("Products table does not exist. Nothing to drop.")
            
    except Exception as e:
        print(f"Error dropping products table: {e}")

if __name__ == "__main__":
    print("Starting process to drop the products table...")
    
    # Confirm before dropping
    confirmation = input("Are you sure you want to DROP the products table? This will delete the table structure and ALL data. (y/n): ")
    
    if confirmation.lower() == 'y':
        drop_products_table()
        print("Operation completed.")
    else:
        print("Operation cancelled.")