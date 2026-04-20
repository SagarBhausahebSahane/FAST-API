from pydantic import BaseModel, Field, EmailStr
from typing import Optional,List
from datetime import datetime
from enum import Enum
import uuid

class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING    = "clothing"
    FOOD        = "food"
    SPORTS      = "sports"

class CreateProduct(BaseModel):
    product_name:str=Field(...,min_length=3,max_length=50)
    product_category:ProductCategory=Field(...)
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_desc:str=Field(...,min_length=15,max_length=100)

class UpdateProduct(BaseModel):
    product_id:str=Field(...)
    product_name:Optional[str] = Field(None, min_length=2, max_length=12)
    product_category:Optional[ProductCategory]=Field(None)
    product_desc:Optional[str]=Field(None,min_length=15,max_length=100)


class AssignedProductToUser(BaseModel):
    user_emails:List[str] = Field(..., min_length=1, example=["jhon@exmple.com","jhon@exmple.com"])
    product_ids:List[str] = Field(..., min_length=1, example=["p1","p2"])