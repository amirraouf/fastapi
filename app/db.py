from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

metadata = MetaData()

# Create a sync engine and session factory

engine = create_engine(
    "sqlite:///./db.sqlite",
    pool_size=10,  # Max connections in the pool
    max_overflow=20,  # Extra connections that can be created beyond `pool_size`
    pool_timeout=30,  # Wait time before giving up on getting a connection
)
session_factory = sessionmaker(engine)
