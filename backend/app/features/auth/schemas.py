from pydantic import BaseModel, EmailStr


class UserGoogleCreate(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
