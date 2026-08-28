# ??? import app.models
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
# ??? from typing import Optional, List
# ??? from typing import Optional, List, Union, Any


class ClothingSimpleSchema(BaseModel):
    id: int
    name: str | None = None
    type: str | None = None
    color: str | None = None
    price: float| None = None
    photo: bytes | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('photo', mode='before')
    @classmethod
    def get_first_photo(cls, v):
        if isinstance(v, list):
            return v[0] if v else None
        return v

class CartItemCreate(BaseModel):
    id_clothing: int
    quantity: int = 1

class FavoriteCreate(BaseModel):
    id_clothing: int

class ClothingDetailSchema(BaseModel):
    id: int
    type: str | None
    color: str | None
    size: str | None
    name: str | None
    composition: str | None

    price: str | float | None

    quantity: int | None
    photo: bytes | None

    model_config = ConfigDict(from_attributes=True)


class ClothingAdditionalSchema(BaseModel):
    color: str
    size: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class ClothingColoredSchema(BaseModel):
    size: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: str
    password: str

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    fathers_name: str | None = None
    phone_number: str | None = None
    city: str | None = None
    street: str | None = None
    house_number: str | None = None


class FavoriteSchema(BaseModel):
    id: int
    clothing: ClothingSimpleSchema

    model_config = ConfigDict(from_attributes=True)


class OrderCatalogSchema(BaseModel):
    id: int
    cost: str | None
    delivery_company: str | None
    date: datetime | None
    items_count: int

    model_config = ConfigDict(from_attributes=True)


class OrderClothingSchema(BaseModel):
    id: int
    name: str | None = None
    price: float| None = None

    model_config = ConfigDict(from_attributes=True)


class OrderContentSchema(BaseModel):
    id: int
    clothing: OrderClothingSchema

    model_config = ConfigDict(from_attributes=True)


class OrderDetailSchema(BaseModel):
    id: int
    cost: float| None = None
    delivery_company: str | None = None
    delivery_type: str | None = None
    postal_number: str | None = None
    date: datetime | None = None
    order_content: list[OrderContentSchema]

    model_config = ConfigDict(from_attributes=True)


class OrderCreateInfoSchema(BaseModel):
    city: str
    street: str
    house_number: str


class OrderCreateSchema(BaseModel):
    cost: str
    delivery_company: str
    delivery_type: str
    postal_number: str
    date: datetime
    id_user: int
    id_clothing: list[int]

    city: str
    street: str
    house_number: str