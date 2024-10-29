# import pytest
# from httpx import AsyncClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.main import app
# from app.models import Base, User, Transfer
# from app.dependencies import get_session
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# import asyncio
#
# # Setup a test database engine
# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
# engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# TestingSessionLocal = sessionmaker(
#     autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
# )
#
#
# # Dependency override for testing
# @pytest.fixture
# async def async_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)  # Create tables for testing
#     async with TestingSessionLocal() as session:
#         yield session
#     await conn.run_sync(Base.metadata.drop_all)  # Drop tables after tests
#
#
# # Use FastAPI dependency override for testing
# @pytest.fixture
# async def client(async_db):
#     app.dependency_overrides[get_session] = lambda: async_db
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client
#
#
# @pytest.mark.asyncio
# async def test_create_transfer(client):
#     # Set up users
#     sender_data = {"name": "Sender", "balance": 1000.0}
#     receiver_data = {"name": "Receiver", "balance": 500.0}
#     sender = await client.post("/users/", json=sender_data)
#     receiver = await client.post("/users/", json=receiver_data)
#
#     # Create transfer
#     transfer_data = {"amount": 100.0, "sender_id": sender.json()["id"], "receiver_id": receiver.json()["id"]}
#     response = await client.post("/transfers/", json=transfer_data)
#     assert response.status_code == 201
#     assert response.json()["amount"] == 100.0
#     assert response.json()["status"] == "PENDING"
#
#
# @pytest.mark.asyncio
# async def test_accept_transfer(client, async_db):
#     # Accept the transfer
#     transfer_id = 1  # Assuming this ID is valid
#     response = await client.post(f"/transfers/{transfer_id}/accept")
#     assert response.status_code == 200
#     transfer_data = response.json()
#     assert transfer_data["status"] == "ACCEPTED"
#
#     # Check sender and receiver balances
#     sender = await client.get(f"/users/{transfer_data['sender_id']}")
#     receiver = await client.get(f"/users/{transfer_data['receiver_id']}")
#     assert sender.json()["balance"] == 900.0  # Deducted amount with fee
#     assert receiver.json()["balance"] == 600.0
#
#
# @pytest.mark.asyncio
# async def test_reject_transfer(client, async_db):
#     # Reject the transfer
#     transfer_id = 2  # Assuming this ID is valid
#     response = await client.post(f"/transfers/{transfer_id}/reject")
#     assert response.status_code == 200
#     assert response.json()["status"] == "REJECTED"
#
#     # Check sender's balance restored
#     sender = await client.get(f"/users/{response.json()['sender_id']}")
#     assert sender.json()["balance"] == 1000.0
#
#
# @pytest.mark.asyncio
# async def test_concurrent_transfers(client, async_db):
#     # Setup sender and receiver
#     sender = await client.post("/users/", json={"name": "Concurrent Sender", "balance": 1000.0})
#     receiver = await client.post("/users/", json={"name": "Concurrent Receiver", "balance": 500.0})
#
#     # Create transfers
#     transfer_data = {"amount": 100.0, "sender_id": sender.json()["id"], "receiver_id": receiver.json()["id"]}
#     transfer_1 = await client.post("/transfers/", json=transfer_data)
#     transfer_2 = await client.post("/transfers/", json=transfer_data)
#
#     # Concurrent acceptance of both transfers
#     async def accept_transfer(transfer_id):
#         return await client.post(f"/transfers/{transfer_id}/accept")
#
#     results = await asyncio.gather(
#         accept_transfer(transfer_1.json()["id"]),
#         accept_transfer(transfer_2.json()["id"]),
#     )
#
#     # Verify one transfer should succeed, one should fail due to insufficient funds
#     success = sum(1 for result in results if result.status_code == 200)
#     assert success == 1  # Only one should succeed
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.event import listens_for
from sqlalchemy.pool import Pool

from app.main import app as main_app
from app.models import User, Transfer
from app.dependencies import get_session
from fastapi.testclient import TestClient

from app.seed import seed

# Setup a test database engine for synchronous testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@listens_for(Pool, "connect", named=True)
def my_on_connect(dbapi_connection, **kw):
    dbapi_connection.execute("pragma foreign_keys=ON")


TestingSessionLocal = sessionmaker(bind=engine)


# Dependency override for synchronous testing
@pytest.fixture(scope="function")
def db():
    transaction = engine.connect().begin()
    session = TestingSessionLocal()

    seed(session)
    yield session
    transaction.rollback()


def get_test_session(session):
    def wrapper():
        yield db
        db.close()

    return wrapper


# Use FastAPI dependency override for testing
@pytest.fixture(scope="function")
def client(db):
    def override_get_session():
        try:
            yield db
        finally:
            db.close()

    main_app.dependency_overrides[get_session] = lambda: override_get_session
    with TestClient(main_app) as client:
        yield client
    # main_app.dependency_overrides.clear()


def test_accept_transfer(client, db):
    # Accept the transfer
    transfer_1 = db.query(Transfer).filter(Transfer.status == "PENDING").first()
    headers = {"user_id": str(transfer_1.receiver_id)}
    response = client.post(f"/transfers/{transfer_1.id}/accept", headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"
    sender = db.query(User).get(transfer_1.sender_id)
    sender.balance = Decimal(sender.balance) + Decimal(transfer_1.amount)
    db.add(sender)
    db.commit()
    response = client.post(f"/transfers/{transfer_1.id}/accept", headers=headers)
    transfer_data = response.json()
    assert response.status_code == 200
    assert transfer_data["status"] == "ACCEPTED"

    # Check sender and receiver balances
    sender = client.get(f"/users/{transfer_data['sender_id']}")
    receiver = client.get(f"/users/{transfer_data['receiver_id']}")
    assert sender.json()["balance"] == 900.0  # Deducted amount with fee
    assert receiver.json()["balance"] == 600.0


def test_reject_transfer(client, db):
    # Reject the transfer
    transfer_id = 2  # Assuming this ID is valid
    response = client.post(f"/transfers/{transfer_id}/reject")
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"

    # Check sender's balance restored
    sender = client.get(f"/users/{response.json()['sender_id']}")
    assert sender.json()["balance"] == 1000.0
