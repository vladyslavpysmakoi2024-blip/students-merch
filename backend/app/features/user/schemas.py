from pydantic import BaseModel, ConfigDict, EmailStr


# Базовий клас лише зі спільними полями
class UserBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None


# Схема оновлення додає до базової решту необов'язкових полів профілю
class UserUpdate(UserBase):
    fathers_name: str | None = None
    city: str | None = None
    street: str | None = None
    house_number: str | None = None
    avatar_url: str | None = None


# Схема створення бере базову і додає обов'язкові пошту та пароль
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Схема відповіді бере УСІ поля з UserUpdate і додає id та email
class UserResponse(UserUpdate):
    id: int
    email: EmailStr
    completed_survey: bool = False
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: str
    password: str


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class UserAndMessageResponse(BaseModel):
    message: str
    user: UserResponse
