from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import case

from app.models import Transfer, TransferStatusEnum, User


def list_transfers(
    session,
    user: User,
    status: TransferStatusEnum = TransferStatusEnum.PENDING,
) -> list[Transfer]:
    """
    List transfers for a user with a given status associated with label "sending" or "receiving".
    """
    transactions = (
        session.query(
            Transfer,
        )
        .options(joinedload(Transfer.sender), joinedload(Transfer.receiver))
        .filter(
            (
                    (Transfer.sender_id == user.id)
                    | (Transfer.receiver_id == user.id))
            & (Transfer.status == status))
        .all()
    )
    return transactions
