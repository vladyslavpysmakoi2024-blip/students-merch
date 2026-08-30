from datetime import datetime
from pydantic import BaseModel, ConfigDict

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