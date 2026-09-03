from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: str
    password: str


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    fathers_name: str | None = None
    phone_number: str | None = None
    city: str | None = None
    street: str | None = None
    house_number: str | None = None
