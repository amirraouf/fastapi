from datetime import datetime

from pydantic import BaseModel

from app.models import TransferStatusEnum


class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Transfer(BaseModel):
    id: int
    status: TransferStatusEnum
    amount: int
    created_at: datetime
    updated_at: datetime
    sender: User
    receiver: User

    class Config:
        from_attributes = True
