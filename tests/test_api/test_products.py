# tests/test_api/test_products.py
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.product import Product

def test_create_product(
    client: TestClient, db: Session
):
    """Test creating a new product."""
    data = {
        "sku": "TEST-PRODUCT-123",
        "name": "New Test Product",
        "description": "Description for new test product",
        "price": 129.99,
        "weight": 1.5,
        "dimensions": '{"length": 15, "width": 10, "height": 5}',
        "is_active": True
    }
    response = client.post("/api/v1/products/", json=data)
    assert response.status_code == 201, response.text
    content = response.json()
    assert content["sku"] == data["sku"]
    assert content["name"] == data["name"]
    assert content["price"] == data["price"]
    assert "id" in content
    
    # Check it was saved to the database
    saved_product = db.query(Product).filter(Product.sku == data["sku"]).first()
    assert saved_product is not None
    assert saved_product.name == data["name"]

def test_create_product_duplicate_sku(
    client: TestClient, db: Session, test_product: Product
):
    """Test that creating a product with duplicate SKU fails."""
    data = {
        "sku": test_product.sku,  # Use existing SKU to trigger duplication error
        "name": "Another Product",
        "description": "This product should not be created",
        "price": 99.99,
        "is_active": True
    }
    
    response = client.post("/api/v1/products/", json=data)
    
    assert response.status_code == 400, response.text
    assert "already exists" in response.json()["detail"]

def test_read_products(client: TestClient, test_product: Product):
    """Test retrieving a list of products."""
    response = client.get("/api/v1/products/")
    
    assert response.status_code == 200, response.text
    content = response.json()
    assert isinstance(content, list)
    assert len(content) >= 1
    
    # Check our test product is in the list
    product_ids = [product["id"] for product in content]
    assert test_product.id in product_ids

def test_read_product(client: TestClient, test_product: Product):
    """Test retrieving a single product by ID."""
    response = client.get(f"/api/v1/products/{test_product.id}")
    
    assert response.status_code == 200, response.text
    content = response.json()
    assert content["id"] == test_product.id
    assert content["sku"] == test_product.sku
    assert content["name"] == test_product.name
    
    # Check the schema is returning all the expected fields
    expected_fields = {"id", "sku", "name", "description", "price", "weight", 
                      "dimensions", "is_active", "created_at"}
    assert set(content.keys()) >= expected_fields

def test_read_product_not_found(client: TestClient):
    """Test retrieving a non-existent product."""
    # Use a very large ID to ensure it doesn't exist
    response = client.get("/api/v1/products/999999")
    
    assert response.status_code == 404, response.text
    assert "not found" in response.json()["detail"].lower()


def test_update_product(
    client: TestClient, db: Session, test_product: Product
):
    """Test updating a product."""
    update_data = {
        "name": "Updated Product Name",
        "description": "Updated description",
        "price": 199.99
    }
    
    response = client.put(
        f"/api/v1/products/{test_product.id}",
        json=update_data
    )
    
    assert response.status_code == 200, response.text
    content = response.json()
    assert content["name"] == update_data["name"]
    assert content["description"] == update_data["description"]
    assert content["price"] == update_data["price"]
    
    # Check original fields remain unchanged
    assert content["sku"] == test_product.sku
    assert content["id"] == test_product.id
    
    # Verify in database
    db.refresh(test_product)
    assert test_product.name == update_data["name"]
    assert test_product.price == update_data["price"]

def test_delete_product(
    client: TestClient, db: Session, test_product: Product
):
    """Test deleting a product (soft delete)."""
    response = client.delete(f"/api/v1/products/{test_product.id}")
    
    assert response.status_code == 204, response.text
    
    # Check in database - should be marked inactive (soft delete)
    db.refresh(test_product)
    assert test_product.is_active is False
