from sqlalchemy import delete

from app.db import session_factory
from app.models import Transfer
from app.models import TransferStatusEnum
from app.models import User


def seed(session=None):
    session = session_factory() if session is None else session

    session.execute(delete(Transfer))
    session.execute(delete(User))

    for i in range(10):
        user = User(username=f"user_{i}", balance=10000 * i)
        session.add(user)

    first_user = session.get(User, 1)
    second_user = session.get(User, 2)

    transfer = Transfer(
        sender=first_user,
        receiver=second_user,
        amount=1000,
        status=TransferStatusEnum.PENDING,
    )
    session.add(transfer)
    transfer = Transfer(
        sender=first_user,
        receiver=second_user,
        amount=1000,
        status=TransferStatusEnum.COMPLETED,
    )
    session.add(transfer)

    session.commit()


if __name__ == "__main__":
    seed()
