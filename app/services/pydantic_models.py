from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models import TransferStatusEnum


class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class TransferValidator(BaseModel):
    id: int
    status: TransferStatusEnum
    amount: Decimal
    created_at: datetime
    updated_at: datetime
    sender: User
    receiver: User

    class Config:
        from_attributes = True


class TransferPageValidator(BaseModel):
    page: int
    limit: int
    transfers: list[TransferValidator]
    total_transfers: int
