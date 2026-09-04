from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Базова схема з усіма спільними полями та логікою фотографій
class ClothingBase(BaseModel):
    id: int
    name: str | None = None
    type: str | None = None
    color: str | None = Field(
        default=None,
        min_length=7,
        max_length=7,
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="HEX color code (e.g., #FFFFFF)",
        examples=["#ffffff"]
    )
    price: Decimal = Field(max_digits=10, decimal_places=2, examples=["0.00"])
    photo: str | None = None
    photos: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def fill_photo(self):
        if not self.photo and self.photos:
            return self.model_copy(update={"photo": self.photos[0]})  # pylint: disable=unsubscriptable-object
        return self


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
    size: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)


# Розширена схема додає лише одне поле до базової
class ClothingAdditionalSchema(ClothingColoredSchema):
    color: str
