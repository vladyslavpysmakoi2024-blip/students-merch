from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime
from typing import Optional, List, Union, Any
import app.models


class ClothingSimpleSchema(BaseModel):
    id: int
    name: Optional[str] = None
    type: Optional[str] = None
    color: Optional[str] = None
    price: Optional[float] = None
    photos: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

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
    photos: list[str] | None

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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    fathers_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None


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
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class OrderContentSchema(BaseModel):
    id: int
    clothing: OrderClothingSchema

    model_config = ConfigDict(from_attributes=True)


class OrderDetailSchema(BaseModel):
    id: int
    cost: Optional[float] = None
    delivery_company: Optional[str] = None
    delivery_type: Optional[str] = None
    postal_number: Optional[str] = None
    date: Optional[datetime] = None
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
    id_clothing: List[int]

    city: str
    street: str
    house_number: str
