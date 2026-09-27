from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.core.colors import color_name
from app.core.types import HexColor


# Базова схема з усіма спільними полями та логікою фотографій
class ClothingBase(BaseModel):
    id: int
    name: str | None = None
    type: str | None = None
    color: HexColor | None = None
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])
    photo: str | None = None
    photos: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def fill_photo(self):
        if not self.photo and self.photos:
            return self.model_copy(update={"photo": self.photos[0]})  # pylint: disable=unsubscriptable-object
        return self

    @computed_field
    @property
    def color_name(self) -> str | None:
        return color_name(self.color)


# Схема для списків не додає нічого нового, лише використовує базу
class ClothingSimpleSchema(ClothingBase):
    pass


# Детальна схема просто бере базу і розширює її своїми специфічними полями
class ClothingDetailSchema(ClothingBase):
    size: str | None = None
    composition: str | None = None
    quantity: int | None = None


# Базова схема для залишків
class ClothingColoredSchema(BaseModel):
    id: int
    size: str | None = None
    quantity: int | None = None

    model_config = ConfigDict(from_attributes=True)


# Розширена схема додає лише одне поле до базової
class ClothingAdditionalSchema(ClothingColoredSchema):
    color: str
