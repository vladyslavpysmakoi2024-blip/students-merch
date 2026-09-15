from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import ResponseStatus


class OrderAddressBase(BaseModel):
    city: str
    street: str
    house_number: str


class OrderDisplayBase(BaseModel):
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])
    delivery_company: str | None = None
    date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# Використовує базову адресу
class OrderCreateInfoSchema(OrderAddressBase):
    pass


# Використовує базову схему створення для онлайн-оплати
class OrderCreateSchema(BaseModel):
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])
    id_clothing: list[int]


# Розширює базу для списку
class OrderCatalogSchema(OrderDisplayBase):
    id: int
    items_count: int


class OrderClothingSchema(BaseModel):
    id: int
    name: str | None = None
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])

    model_config = ConfigDict(from_attributes=True)


class OrderContentSchema(BaseModel):
    id: int
    clothing: OrderClothingSchema

    model_config = ConfigDict(from_attributes=True)


# Розширює базу для детального перегляду
class OrderDetailSchema(OrderDisplayBase):
    id: int
    delivery_type: str | None = None
    postal_number: str | None = None
    order_content: list[OrderContentSchema]


class OrderCreateResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str
    payment_url: str | None = None


class MonobankWebhook(BaseModel):
    invoiceId: str | None = None
    status: str | None = None
    amount: int | float | None = None
    reference: str | None = None

    model_config = ConfigDict(extra="ignore")
