from pydantic import BaseModel, ConfigDict, field_validator

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