from pydantic import BaseModel, ConfigDict
from app.features.clothing.schemas import ClothingSimpleSchema


class CartItemCreate(BaseModel):
    id_clothing: int
    quantity: int = 1


class FavoriteCreate(BaseModel):
    id_clothing: int
