from fastapi import Depends
from option import Option
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import case
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_session import get_session
from app.models import Transfer, TransferStatusEnum, User


def list_transfers(
    session = Depends(get_session),
    user: User = Depends(get_current_user),
    status: TransferStatusEnum = TransferStatusEnum.PENDING,
) -> Option[list[Transfer]]:
    """
    List transfers for a user with a given status.
    """
    transactions = (
        session.query(
            Transfer,
            case(
                [(Transfer.sender_id == user.id, "sending")],
                else_="receiving"
            ).label("label")
        )
        .options(joinedload(Transfer.sender), joinedload(Transfer.receiver))
        .filter((Transfer.sender_id == user.id) | (Transfer.receiver_id == user.id))
        .all()
    )
    return Option(transactions)