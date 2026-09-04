from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.schemas import ResponseStatus
from app.core.types import HexColor


class CartItemCreate(BaseModel):
    id_clothing: int
    quantity: int = 1


class CartItemResponse(BaseModel):
    id: int
    cart_id: int | None = None
    product_id: int
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])
    size: str
    color: HexColor | None = None
    photo: str | None = Field(
        default=None,
        description="URL-address to photo (HTTPS)",
        examples=["https://example.com/images/tshirt_front.jpg"],
    )
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartAddResponse(BaseModel):
    status: ResponseStatus
    cart_item_id: int | None = None
    new_quantity: int | None = None


class CartUpdateResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.UPDATED
    new_quantity: int


class CartDeleteResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.DELETED
    cart_id: int
