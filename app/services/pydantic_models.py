from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models import TransferStatusEnum


class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class TransferLabel(str, Enum):
    sending = 'sending'
    receiving = 'receiving'


class Transfer(BaseModel):
    id: int
    status: TransferStatusEnum
    amount: int
    created_at: datetime
    updated_at: datetime
    sender: User
    receiver: User
    label: Optional[TransferLabel]

    class Config:
        from_attributes = True
