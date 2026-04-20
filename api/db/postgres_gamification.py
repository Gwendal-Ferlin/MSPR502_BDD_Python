from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.config import settings

engine_gamification = create_engine(
    settings.postgres_gamification_url,
    pool_pre_ping=True,
)
SessionGamification = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_gamification
)


def get_session_gamification() -> Session:
    session = SessionGamification()
    try:
        yield session
    finally:
        session.close()

