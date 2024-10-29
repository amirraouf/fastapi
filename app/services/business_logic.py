from decimal import Decimal
from typing import List, Any, Dict
from sqlalchemy import func, desc

from fastapi import HTTPException
from option import Ok, Err, Result

from app.models import Transfer, TransferStatusEnum, User
from app.services.selectors import (
    list_transfers,
    get_user_by_id,
    get_transfer_by_id,
    count_transfers_by_user,
)


def list_transfer_logic(
    session, user, status, **kwargs
) -> Result[dict[str, int | list[Transfer]], Any]:
    page = kwargs.get("page", 1)
    limit = kwargs.get("limit", 10)
    offset = (page - 1) * limit

    transactions = list_transfers(session, user, status, offset=offset, limit=limit)
    total_transfers = count_transfers_by_user(session, user, status)

    return Ok(
        {
            "page": page,
            "limit": limit,
            "total_transfers": total_transfers,
            "transfers": transactions,
        }
    )


def accept_transfer(session, transfer_id, user_id) -> Result[dict, HTTPException]:
    """
    Allows the receiver to accept a transfer,
    moving funds from the sender’s balance to the receiver’s balance minus a 2% fee.
    """
    with session.begin_nested():
        transfer = get_transfer_by_id(session, transfer_id)
        if (
            not transfer
            or transfer.receiver_id != user_id
            or transfer.status != TransferStatusEnum.PENDING
        ):
            return Err(HTTPException(status_code=403, detail="Cannot accept transfer"))
        fee = Decimal(transfer.amount) * Decimal("0.02")
        net_amount = Decimal(transfer.amount) - fee
        sender = get_user_by_id(session, transfer.sender_id, lock_for_update=True)
        receiver = get_user_by_id(session, transfer.receiver_id, lock_for_update=True)
        if sender.balance < transfer.amount:
            return Err(HTTPException(status_code=400, detail="Insufficient funds"))
        sender.balance -= transfer.amount
        receiver.balance += net_amount
        transfer.status = TransferStatusEnum.COMPLETED
        session.add(transfer)
        session.add(sender)
        session.add(receiver)
        session.commit()
        return Ok({"status": "Transfer accepted"})


def reject_transfer(session, transfer_id, user_id):
    transfer = get_transfer_by_id(session, transfer_id)
    if (
        not transfer
        or transfer.receiver_id != user_id
        or transfer.status != TransferStatusEnum.PENDING
    ):
        return Err(HTTPException(status_code=403, detail="Cannot reject transfer"))
    transfer.status = TransferStatusEnum.REJECTED
    session.add(transfer)
    session.commit()
    return Ok({"status": "Transfer rejected"})


def get_transfer(
    session, transfer_id, request_user_id
) -> Result[Transfer, HTTPException]:
    """
    Retrieve a specific transfer by ID, ensuring the user is authorized (either the sender or receiver).
    """
    transfer = get_transfer_by_id(session, transfer_id)
    if not transfer:
        return Err(HTTPException(status_code=404, detail="Transfer not found"))
    if request_user_id not in [transfer.sender_id, transfer.receiver_id]:
        return Err(HTTPException(status_code=403, detail="Access denied"))
    return Ok(transfer)


def deposit_balance(session, user_id, amount: Decimal) -> Result[dict, HTTPException]:
    user = get_user_by_id(session, user_id, lock_for_update=True)
    if user is None:
        return Err(HTTPException(status_code=404, detail="User not found"))

    user.balance += amount
    session.add(user)
    session.commit()
    return Ok({"status": "Deposit successful", "balance": user.balance})


def withdraw_amount(session, user_id, amount: Decimal) -> Result[dict, HTTPException]:
    user = get_user_by_id(session, user_id, lock_for_update=True)
    if user.balance < amount:
        return Err(HTTPException(status_code=400, detail="Insufficient funds"))
    user.balance -= amount
    session.add(user)
    session.commit()
    return Ok({"status": "Withdrawal successful", "balance": user.balance})


def transfers_leaderboard(session, by) -> Result[List[Dict[str, Any]], HTTPException]:
    """
    Returns a list of users with the highest number of transfers.
    """
    if by == "count":
        result = (
            session.query(
                User.id, User.username, func.count(Transfer.id).label("transfer_count")
            )
            .join(
                Transfer,
                (Transfer.sender_id == User.id) | (Transfer.receiver_id == User.id),
            )
            .group_by(User.id)
            .order_by(desc("transfer_count"))
            .limit(10)
            .all()
        )
    elif by == "amount":
        result = (
            session.query(
                User.id,
                User.username,
                func.sum(Transfer.amount).label("total_transferred"),
            )
            .join(
                Transfer,
                (Transfer.sender_id == User.id) | (Transfer.receiver_id == User.id),
            )
            .group_by(User.id)
            .order_by(desc("total_transferred"))
            .limit(10)
            .all()
        )
    else:
        return Err(HTTPException(status_code=400, detail="Invalid 'by' parameter"))
    result = [row._mapping for row in result]
    return Ok(result)
