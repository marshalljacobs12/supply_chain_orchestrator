# app/schemas/product.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    weight: Optional[float] = None
    dimensions: Optional[str] = None  # JSON string
    is_active: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    is_active: Optional[bool] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True  # For Pydantic v1
        from_attributes = True  # For Pydantic v2

class ProductDetail(Product):
    # total_inventory: int = 0
    # stock_status: str = "Unknown"
    # suppliers: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        orm_mode = True  # For Pydantic v1
        from_attributes = True  # For Pydantic v2