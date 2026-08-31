from decimal import Decimal
from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    id_clothing: int
    quantity: int = 1


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=['0.00'])
    size: str
    color: str


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)
