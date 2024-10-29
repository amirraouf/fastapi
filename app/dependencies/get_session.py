from app.db import session_factory


def get_session():
    with session_factory() as session:
        yield session
        session.close()
