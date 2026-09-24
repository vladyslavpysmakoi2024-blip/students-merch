from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.core.types import HexColor
from app.features.order.schemas import OrderDetailSchema
from app.features.promo.schemas import PromoResponse

PhotoList = Annotated[list[str], AfterValidator(lambda photos: [photo for photo in photos if photo])]


class ClothingCreate(BaseModel):
    name: str | None = None
    type: str | None = None
    color: HexColor | None = None
    size: str | None = None
    composition: str | None = None
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2, examples=["0.00"])
    quantity: int | None = Field(default=None, ge=0)
    photos: PhotoList = []

    model_config = ConfigDict(str_strip_whitespace=True)


class ClothingBulkCreate(BaseModel):
    items: list[ClothingCreate] = Field(min_length=1, max_length=100)


class ClothingIds(BaseModel):
    ids: list[int] = Field(min_length=1)


class ClothingBulkUpdate(ClothingIds):
    name: str | None = None
    type: str | None = None
    color: HexColor | None = None
    composition: str | None = None
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2, examples=["0.00"])
    quantity: int | None = Field(default=None, ge=0)
    photos: PhotoList | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def check_price(self):
        if "price" in self.model_fields_set and self.price is None:
            raise ValueError("price cannot be empty")
        return self


class PromoCreate(BaseModel):
    promo: str = Field(min_length=1, max_length=50)
    date_start: date
    date_end: date
    discount_percent: Decimal = Field(gt=0, le=100, max_digits=5, decimal_places=2, examples=["0.00"])

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def check_dates(self):
        if self.date_end < self.date_start:
            raise ValueError("date_end must not be earlier than date_start")
        return self


class PromoAdminSchema(PromoResponse):
    id: int
    date_start: date
    date_end: date


class OrderUserSchema(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderAdminSchema(OrderDetailSchema):
    user: OrderUserSchema | None = None
