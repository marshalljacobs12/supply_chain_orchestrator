# tests/conftest.py
import os
from typing import Generator
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database

from app.main import app
from app.database import get_db, Base
from app.models.product import Product

# Database connection parameters
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
TEST_DB_NAME = "test_supply_chain_db"

# Construct the database URL
TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}",
)

def create_test_database():
    """Create test database if it doesn't exist."""
    try:
        # First try to connect to the postgres database to check/create our test db
        postgres_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
        postgres_engine = create_engine(postgres_url)
        
        # Check if our test database exists
        if not database_exists(TEST_DB_URL):
            # Create the test database
            print(f"Creating test database: {TEST_DB_NAME}")
            create_database(TEST_DB_URL)
            print(f"Test database created successfully")
        
        # Connect to our test database
        test_engine = create_engine(TEST_DB_URL)
        
        # Create tables
        Base.metadata.create_all(bind=test_engine)
        
        # Check if Product table was created
        inspector = inspect(test_engine)
        if 'product' not in inspector.get_table_names():
            print("Product table not found, creating tables...")
            Base.metadata.create_all(bind=test_engine)
            
        return test_engine
    except Exception as e:
        print(f"Error setting up test database: {e}")
        raise

# Try to create the test database
try:
    engine = create_test_database()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Failed to set up database: {e}")
    print("Falling back to SQLite for testing")
    # Fallback to SQLite for testing if PostgreSQL is not available
    TEST_DB_URL = "sqlite:///./test.db"
    engine = create_engine(TEST_DB_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database session for a test."""
    # Create tables (ensure they exist)
    Base.metadata.create_all(bind=engine)
    
    # Create session
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
            session.flush()
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # Rollback and clean up
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client for API tests."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def test_product(db: Session) -> Product:
    """Create a test product."""
    product_data = {
        "sku": "TEST-PROD-001",
        "name": "Test Product",
        "description": "Test product description",
        "price": 99.99,
        "weight": 1.0,
        "dimensions": '{"length": 10, "width": 10, "height": 10}',
        "is_active": True
    }
    
    # Check if product already exists
    product = db.query(Product).filter(Product.sku == product_data["sku"]).first()
    if not product:
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
    
    return product