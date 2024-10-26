from fastapi import Depends
from fastapi import FastAPI
from sqlalchemy.orm import joinedload

from app.db import session_factory
from app.dependencies.get_current_user import get_current_user
from app.models import Transfer
from app.models import TransferStatusEnum
from app.models import User
from app.pydantic_models import Transfer as TransferPydantic


app = FastAPI()


@app.get("/transfers", response_model=list[TransferPydantic])
async def list_transfers(
    current_user: User = Depends(get_current_user),
    status: TransferStatusEnum = TransferStatusEnum.PENDING,
):
    with session_factory() as session:
        return (
            session.query(Transfer)
            .options(joinedload(Transfer.sender), joinedload(Transfer.receiver))
            .filter(Transfer.receiver == current_user, Transfer.status == status)
            .all()
        )
