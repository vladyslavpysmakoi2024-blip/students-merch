from pydantic import BaseModel, ConfigDict, Field
from app.features.clothing.schemas import ClothingSimpleSchema


class CartItemCreate(BaseModel):
    id_clothing: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemResponse(BaseModel):
    cart_id: int
    product_id: int
    name: str | None = None
    price: float | None = None
    size: str | None = None
    color: str | None = None
    photo: str | None = None
    quantity: int


class FavoriteCreate(BaseModel):
    id_clothing: int
