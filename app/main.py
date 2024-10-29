from decimal import Decimal

from fastapi import FastAPI, Depends, Query, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.db import session_factory
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_session import get_session
from app.models import TransferStatusEnum
from app.models import User
from app.scheme import custom_openapi
from app.services.business_logic import (
    list_transfer_logic,
    get_transfer,
    accept_transfer,
    deposit_balance,
    reject_transfer,
    transfers_leaderboard,
)
from app.services.pydantic_models import TransferValidator, TransferPageValidator

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.openapi = custom_openapi(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/transfers", response_model=TransferPageValidator)
@limiter.limit("5/minute")
async def list_transfers_api(
    request: Request,
    session: session_factory = Depends(get_session),
    current_user: User = Depends(get_current_user),
    status: TransferStatusEnum = None,
    page: int = Query(1, ge=1),  # Page number, defaults to 1
    limit: int = Query(10, ge=1),  # Limit number of items per page, defaults to 10
):
    result = list_transfer_logic(session, current_user, status, page=page, limit=limit)
    return result.unwrap()


@app.get("/transfers/{transfer_id}", response_model=TransferValidator)
def get_transfer_api(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    session: session_factory = Depends(get_session),
):
    """
    Retrieve a specific transfer by ID, ensuring the user is authorized (either the sender or receiver).
    """
    transfer = get_transfer(session, transfer_id, current_user.id)
    if transfer.is_err:
        raise transfer.unwrap_err()
    return transfer.unwrap()


@app.post("/transfers/{transfer_id}/accept")
def accept_transfer_api(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    session: session_factory = Depends(get_session),
):
    """
    Allows the receiver to accept a transfer, moving funds from the sender’s balance to the receiver’s balance minus a 2% fee.
    """
    result = accept_transfer(session, transfer_id, current_user.id)
    if result.is_err:
        raise result.unwrap_err()
    return result.unwrap()


@app.post("/transfers/{transfer_id}/reject")
def reject_transfer_api(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    session: session_factory = Depends(get_session),
):
    """
    Rejects the transfer, returning the amount to the sender’s balance.
    """
    result = reject_transfer(session, transfer_id, current_user.id)
    if result.is_err:
        raise result.unwrap_err()
    return result.unwrap()


@app.post("/deposit")
def deposit_api(
    amount: Decimal,
    current_user: User = Depends(get_current_user),
    session: session_factory = Depends(get_session),
):
    """Deposits money into the user's balance."""
    result = deposit_balance(session, current_user.id, amount)
    if result.is_err:
        raise result.unwrap_err()
    return result.unwrap()


@app.post("/withdraw")
def withdraw_api(
    amount: Decimal,
    current_user: User = Depends(get_current_user),
    session: session_factory = Depends(get_session),
):
    """Withdraws money from the user’s balance, ensuring they have enough funds."""
    result = deposit_balance(session, current_user.id, amount)
    if result.is_err:
        raise result.unwrap_err()
    return result.unwrap()


@app.get("/leaderboard/top-transfers")
def get_top_transfers_api(
    limit: int = 10, by: str = "count", session: session_factory = Depends(get_session)
):
    """
    Returns the top users who have sent or received the most transfers.
    Allows filtering by the number of transfers or total transferred amount.
    """
    results = transfers_leaderboard(session, by)
    if results.is_err:
        raise results.unwrap_err()
    return results.unwrap()
