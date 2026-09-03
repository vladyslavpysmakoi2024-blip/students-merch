from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ClothingSimpleSchema(BaseModel):
    id: int
    name: str | None = None
    type: str | None = None
    color: str | None = None
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])
    photos: list[str] | None = None
    photo: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def fill_photo(self):
        if not self.photo and self.photos:
            return self.model_copy(update={"photo": self.photos[0]})
        return self


class ClothingDetailSchema(BaseModel):
    id: int
    type: str | None
    color: str | None
    size: str | None
    name: str | None
    composition: str | None

    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])

    quantity: int | None
    photo: str | None = None
    photos: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def fill_photo(self):
        if not self.photo and self.photos:
            return self.model_copy(update={"photo": self.photos[0]})
        return self


class ClothingAdditionalSchema(BaseModel):
    color: str
    size: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class ClothingColoredSchema(BaseModel):
    size: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)
