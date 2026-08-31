from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_validator, Field

class ClothingSimpleSchema(BaseModel):
    id: int
    name: str | None = None
    type: str | None = None
    color: str | None = None
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=['0.00'])
    photo: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('photo', mode='before')
    @classmethod
    def get_first_photo(cls, v):
        if isinstance(v, list):
            return v[0] if v else None
        return v

class ClothingDetailSchema(BaseModel):
    id: int
    type: str | None
    color: str | None
    size: str | None
    name: str | None
    composition: str | None

    price: Decimal = Field(max_digits=10, decimal_places=2, examples=['0.00'])

    quantity: int | None
    photo: str | None = None
    photos: list[str] | None = None

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