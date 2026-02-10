from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.config import settings

engine_utilisateur = create_engine(
    settings.postgres_utilisateur_url,
    pool_pre_ping=True,
)
SessionUtilisateur = sessionmaker(autocommit=False, autoflush=False, bind=engine_utilisateur)


def get_session_utilisateur() -> Session:
    session = SessionUtilisateur()
    try:
        yield session
    finally:
        session.close()
