from pydantic import BaseModel, ConfigDict

from app.core.schemas import ResponseStatus
from app.features.clothing.schemas import ClothingSimpleSchema


class FavoriteCreate(BaseModel):
    id_clothing: int


class FavoriteAddResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.SUCCESS
    favorite_id: int


class FavoriteDeleteResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str


# Схема для отримання списку
class FavoriteSchema(BaseModel):
    id: int
    clothing: ClothingSimpleSchema
    model_config = ConfigDict(from_attributes=True)
