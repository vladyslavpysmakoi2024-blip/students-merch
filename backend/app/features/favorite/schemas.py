from pydantic import BaseModel, ConfigDict
from app.features.cart.schemas import ClothingSimpleSchema

class FavoriteCreate(BaseModel):
    id_clothing: int


class FavoriteResponse(BaseModel):
    status: str
    message: str | None
    favorite_id: int


class FavoriteSchema(BaseModel):
    id: int
    clothing: ClothingSimpleSchema
    model_config = ConfigDict(from_attributes=True)