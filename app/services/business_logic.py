from option import Option, Ok

from .selectors import list_transfers
from ..models import Transfer


def list_transfer_logic(session, user, status) -> Option[list[Transfer]]:
    transactions = list_transfers(session, user, status)
    return Ok(transactions)
