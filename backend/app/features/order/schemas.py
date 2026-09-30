from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import ResponseStatus


class OrderAddressBase(BaseModel):
    city: str
    street: str
    house_number: str


class OrderDisplayBase(BaseModel):
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])
    delivery_company: str | None = None
    date: datetime | None = None

    status: str

    @field_validator("status", mode="before")
    @classmethod
    def extract_status_string(cls, value) -> str:
        if hasattr(value, "data"):
            return value.data
        return value

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
    type: str | None = None
    color: str | None = None
    size: str | None = None
    photos: list[str] | None = None

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
    invoice_id: str | None = None
    order_content: list[OrderContentSchema]


class ReceiptItemSchema(BaseModel):
    id: int
    name: str
    type: str | None = None
    color: str | None = None
    size: str | None = None
    price: float
    quantity: int = 1
    total: float
    photo: str | None = None


class ReceiptCustomerSchema(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    street: str | None = None
    house_number: str | None = None


class OrderReceiptSchema(BaseModel):
    order_id: int
    receipt_number: str
    created_at: datetime | None = None
    status: str
    payment_method: str = "Monobank Онлайн"
    invoice_id: str | None = None
    monobank_receipt_id: str | None = None
    monobank_receipt_url: str | None = None
    customer: ReceiptCustomerSchema
    delivery_company: str | None = None
    delivery_type: str | None = None
    postal_number: str | None = None
    items: list[ReceiptItemSchema]
    subtotal: float
    total_amount: float
    currency: str = "UAH"
    store_name: str = "Students Merch Shop"
    store_address: str = "м. Львів, вул. Степана Бандери, 12 (НУ «Львівська Політехніка»)"


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
