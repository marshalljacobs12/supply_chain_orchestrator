#!/usr/bin/env python3
# scripts/seed_products.py

import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, MetaData, Table, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os

# Database connection 
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/supply_chain_db")
engine = create_engine(DB_URL)
metadata = MetaData()
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Product model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    weight = Column(Float)
    dimensions = Column(String)
    # category_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Sample products (without category references)
PRODUCTS = [
    {
        "sku": "E-PHONE-001",
        "name": "Smartphone XS",
        "description": "Latest smartphone with 6.5 inch display and 128GB storage",
        "price": 799.99,
        "weight": 0.17,
        "dimensions": "{\"length\": 14.7, \"width\": 7.1, \"height\": 0.8}",
        "is_active": True
    },
    {
        "sku": "E-LAPTOP-001",
        "name": "UltraBook Pro",
        "description": "Lightweight laptop with 16GB RAM and 512GB SSD",
        "price": 1299.99,
        "weight": 1.3,
        "dimensions": "{\"length\": 30.5, \"width\": 21.0, \"height\": 1.5}",
        "is_active": True
    },
    {
        "sku": "E-HEAD-001",
        "name": "Noise Cancelling Headphones",
        "description": "Over-ear headphones with 20-hour battery life",
        "price": 249.99,
        "weight": 0.25,
        "dimensions": "{\"length\": 19.0, \"width\": 16.5, \"height\": 8.0}",
        "is_active": True
    },
    {
        "sku": "C-TSHIRT-001",
        "name": "Premium Cotton T-Shirt",
        "description": "Soft, breathable cotton t-shirt in multiple colors",
        "price": 24.99,
        "weight": 0.2,
        "dimensions": "{\"length\": 70.0, \"width\": 50.0, \"height\": 1.0}",
        "is_active": True
    },
    {
        "sku": "C-JEANS-001",
        "name": "Slim Fit Jeans",
        "description": "Classic 5-pocket jeans with stretch denim",
        "price": 59.99,
        "weight": 0.5,
        "dimensions": "{\"length\": 100.0, \"width\": 30.0, \"height\": 2.0}",
        "is_active": True
    },
    {
        "sku": "HK-BLENDER-001",
        "name": "High-Speed Blender",
        "description": "1000W blender with multiple speed settings",
        "price": 79.99,
        "weight": 3.2,
        "dimensions": "{\"length\": 40.0, \"width\": 20.0, \"height\": 20.0}",
        "is_active": True
    },
    {
        "sku": "HK-POT-001",
        "name": "Non-Stick Cooking Pot",
        "description": "10-inch cooking pot with tempered glass lid",
        "price": 34.99,
        "weight": 1.5,
        "dimensions": "{\"length\": 25.0, \"width\": 25.0, \"height\": 15.0}",
        "is_active": True
    },
    {
        "sku": "SO-YOGA-001",
        "name": "Yoga Mat",
        "description": "Non-slip yoga mat with carrying strap",
        "price": 29.99,
        "weight": 1.0,
        "dimensions": "{\"length\": 180.0, \"width\": 60.0, \"height\": 0.5}",
        "is_active": True
    },
    {
        "sku": "SO-BOTTLE-001",
        "name": "Insulated Water Bottle",
        "description": "24oz stainless steel water bottle",
        "price": 19.99,
        "weight": 0.3,
        "dimensions": "{\"length\": 25.0, \"width\": 8.0, \"height\": 8.0}",
        "is_active": True
    },
    {
        "sku": "BP-CREAM-001",
        "name": "Moisturizing Face Cream",
        "description": "Hydrating face cream for all skin types",
        "price": 14.99,
        "weight": 0.1,
        "dimensions": "{\"length\": 7.0, \"width\": 7.0, \"height\": 5.0}",
        "is_active": True
    }
]

def create_tables():
    """Create tables if they don't exist."""
    try:
        # Check if products table exists
        insp = engine.dialect.has_table(engine.connect(), "products")
        if not insp:
            print("Creating products table...")
            # Create all tables defined in Base
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
        else:
            print("Products table already exists.")
    except Exception as e:
        print(f"Error creating tables: {e}")

def seed_products():
    """Seed the products table with sample data."""
    db = SessionLocal()
    try:
        # Create products
        print("Creating products...")
        for product_data in PRODUCTS:
            # Check if product already exists
            if not db.query(Product).filter(Product.sku == product_data["sku"]).first():
                now = datetime.datetime.now()
                product = Product(
                    **product_data,
                    created_at=now,
                    updated_at=now
                )
                db.add(product)
                print(f"Added product: {product_data['name']}")
            else:
                print(f"Product already exists: {product_data['name']}")
        
        db.commit()
        print("Products seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding products: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting product seed process...")
    create_tables()
    seed_products()
    print("Process completed.")