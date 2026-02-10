from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.config import settings

engine_sante = create_engine(
    settings.postgres_sante_url,
    pool_pre_ping=True,
)
SessionSante = sessionmaker(autocommit=False, autoflush=False, bind=engine_sante)


def get_session_sante() -> Session:
    session = SessionSante()
    try:
        yield session
    finally:
        session.close()
