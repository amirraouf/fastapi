import enum
from datetime import datetime
from datetime import timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from app.db import metadata


class Base(DeclarativeBase):
    metadata = metadata


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    balance = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, balance={self.balance})>"


class TransferStatusEnum(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True)
    # FIXME: There's a bug with both created_at and updated_at fields, can you fix it?
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    amount = Column(Integer, nullable=False)
    status = Column(
        Enum(TransferStatusEnum), nullable=False, default=TransferStatusEnum.PENDING
    )
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    sender = relationship("User", foreign_keys="Transfer.sender_id")
    receiver = relationship("User", foreign_keys="Transfer.receiver_id")

    def __repr__(self) -> str:
        return f"<Transfer(id={self.id}, sender={self.sender}, receiver={self.receiver}, amount={self.amount}, status:{self.status}, created_at: {self.created_at}>"
