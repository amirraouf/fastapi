from sqlalchemy.orm import joinedload

from app.models import Transfer, TransferStatusEnum, User


def count_transfers_by_user(
    session, user: User, status: TransferStatusEnum = None
) -> int:
    filters = (Transfer.sender_id == user.id) | (Transfer.receiver_id == user.id)
    if status:
        filters &= Transfer.status == status

    qry = (
        session.query(
            Transfer,
        )
        .options(joinedload(Transfer.sender), joinedload(Transfer.receiver))
        .filter(filters)
    )
    count = qry.count()
    return count


def list_transfers(
    session,
    user: User,
    status: TransferStatusEnum,
    offset: int = 1,
    limit: int = 10,
) -> list[Transfer]:
    """
    List transfers for a user with a given status associated with label "sending" or "receiving".
    """
    filters = (Transfer.sender_id == user.id) | (Transfer.receiver_id == user.id)

    if status:
        filters &= Transfer.status == status

    transactions = (
        session.query(
            Transfer,
        )
        .options(joinedload(Transfer.sender), joinedload(Transfer.receiver))
        .filter(filters)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return transactions


def get_user_by_id(session, user_id, lock_for_update=False) -> User:
    qry = session.query(User).filter(User.id == user_id)
    if lock_for_update:
        return qry.with_for_update().first()
    return qry.first()


def get_transfer_by_id(session, transfer_id) -> Transfer:
    return session.query(Transfer).filter(Transfer.id == transfer_id).first()
