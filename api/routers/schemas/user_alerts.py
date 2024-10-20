from pydantic import BaseModel


class UserAlertCreate(BaseModel):
    id: int


class UserAlertUpdate(BaseModel): ...
