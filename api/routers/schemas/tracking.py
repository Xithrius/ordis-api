from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Order(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: int
    platinum_threshold: int
    minimum_quantity: int
    item_id: str
    notify_users: list[int]


class OrderCreate(BaseModel):
    user_id: int
    platinum_threshold: int
    minimum_quantity: int
    item_id: str
    notify_users: list[int] = []


class OrderUpdate(BaseModel):
    pass
