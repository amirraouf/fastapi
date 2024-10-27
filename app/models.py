import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import sqlite
from app.db import metadata


class Base(DeclarativeBase):
    metadata = metadata


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    balance = Column(sqlite.REAL(precision=18, decimal_return_scale=2), nullable=False, default=Decimal(0))

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, balance={self.balance})>"


class TransferStatusEnum(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    amount = Column(sqlite.REAL(precision=18, decimal_return_scale=2), nullable=False, default=Decimal(0))
    status = Column(
        Enum(TransferStatusEnum), nullable=False, default=TransferStatusEnum.PENDING
    )
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    sender = relationship("User", foreign_keys="Transfer.sender_id")
    receiver = relationship("User", foreign_keys="Transfer.receiver_id")

    def __repr__(self) -> str:
        return f"<Transfer(id={self.id}, sender={self.sender}, receiver={self.receiver}, amount={self.amount}, status:{self.status}, created_at: {self.created_at}>"
