from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PromoApply(BaseModel):
    promo: str = Field(min_length=1, max_length=50)


class PromoResponse(BaseModel):
    promo: str
    discount_percent: Decimal = Field(max_digits=5, decimal_places=2, examples=['0.00'])

    model_config = ConfigDict(from_attributes=True)
