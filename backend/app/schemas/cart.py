from pydantic import BaseModel, ConfigDict
from app.schemas.clothing import ClothingSimpleSchema


class CartItemCreate(BaseModel):
    id_clothing: int
    quantity: int = 1


class FavoriteCreate(BaseModel):
    id_clothing: int


class FavoriteSchema(BaseModel):
    id: int
    clothing: ClothingSimpleSchema
    model_config = ConfigDict(from_attributes=True)