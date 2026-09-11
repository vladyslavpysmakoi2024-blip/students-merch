from enum import StrEnum

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class ResponseStatus(StrEnum):
    SUCCESS = "success"
    UPDATED = "updated"
    DELETED = "deleted"
    ERROR = "error"
