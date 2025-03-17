# app/api/endpoints/products.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import product as product_models
from app.schemas import product as product_schemas
# from app.services import inventory_service

router = APIRouter()

@router.get("/", response_model=List[product_schemas.Product])
def get_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: bool = True
):
    """
    Retrieve products with optional filtering.
    
    - **skip**: Number of products to skip (pagination)
    - **limit**: Maximum number of products to return
    - **name**: Optional filter by product name (partial match)
    - **category_id**: Optional filter by category ID
    - **is_active**: Filter by active status
    """
    query = db.query(product_models.Product)
    
    if name:
        query = query.filter(product_models.Product.name.ilike(f"%{name}%"))
    if category_id:
        query = query.filter(product_models.Product.category_id == category_id)
    if is_active is not None:
        query = query.filter(product_models.Product.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=product_schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: product_schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product.

    The request body should contain:
    - **sku**: Stock Keeping Unit (unique)
    - **name**: Product name
    - **description**: Optional product description
    - **price**: Product price
    - **weight**: Optional product weight
    - **dimensions**: Optional product dimensions as JSON string
    - **category_id**: Optional category ID
    - **is_active**: Whether the product is active (default: true)
    """
    # Check if product with same SKU already exists
    existing_product = db.query(product_models.Product).filter(
        product_models.Product.sku == product.sku
    ).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU {product.sku} already exists"
        )
    
    # Create new product
    db_product = product_models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=product_schemas.ProductDetail)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific product including inventory levels.
    
    - **product_id**: ID of the product to retrieve
    """
    db_product = db.query(product_models.Product).filter(
        product_models.Product.id == product_id
    ).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Enhance the response with inventory information
    product_detail = product_schemas.ProductDetail.from_orm(db_product)
    # WAIT TILL ADDING INVENTORY_SERVICE
    # product_detail.total_inventory = inventory_service.get_total_inventory(db, product_id)
    # product_detail.stock_status = inventory_service.get_stock_status(db, product_id)
    
    # GET SUPPLIER INFORMATION (LIMITED INFO FOR SECURITY)

    return product_detail

@router.put("/{product_id}", response_model=product_schemas.Product)
def update_product(
    product_id: int,
    product_update: product_schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a product.

    - **product_id**: ID of the product to update
    
    The request body may contain any of these fields:
    - **name**: New product name
    - **description**: New product description
    - **price**: New product price
    - **weight**: New product weight
    - **dimensions**: New product dimensions
    - **category_id**: New category ID
    - **is_active**: New active status
    """
    db_product = db.query(product_models.Product).filter(
        product_models.Product.id == product_id
    ).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update product fields
    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# ADDING DELETE
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product (soft delete by setting is_active to false).
    
    - **product_id**: ID of the product to delete
    """
    db_product = db.query(product_models.Product).filter(
        product_models.Product.id == product_id
    ).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    db_product.is_active = False
    db.commit()
    return None