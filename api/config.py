from pathlib import Path

from pydantic_settings import BaseSettings

# Racine du dépôt (parent de api/) — pour charger .env même si uvicorn est lancé depuis un autre cwd
_REPO_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # PostgreSQL Utilisateur
    postgres_utilisateur_host: str = "localhost"
    postgres_utilisateur_port: int = 5432
    postgres_utilisateur_user: str = "utilisateur_user"
    postgres_utilisateur_password: str = ""
    postgres_utilisateur_db: str = "utilisateur_db"

    # PostgreSQL Santé
    postgres_sante_host: str = "localhost"
    postgres_sante_port: int = 5433
    postgres_sante_user: str = "sante_user"
    postgres_sante_password: str = ""
    postgres_sante_db: str = "sante_db"

    # PostgreSQL Gamification
    postgres_gamification_host: str = "localhost"
    postgres_gamification_port: int = 5434
    postgres_gamification_user: str = "gamification_user"
    postgres_gamification_password: str = ""
    postgres_gamification_db: str = "gamification_db"

    # MongoDB Logs
    mongodb_logs_host: str = "localhost"
    mongodb_logs_port: int = 27017
    mongodb_logs_db: str = "logs_config"

    # MongoDB Reco
    mongodb_reco_host: str = "localhost"
    mongodb_reco_port: int = 27018
    mongodb_reco_db: str = "reco"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Chiffrement au repos (Fernet) pour compte_utilisateur, profil_sante, suivi_biometrique, ref_restriction
    # Générer : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    data_encryption_key: str = ""

    # Rate limiting (SlowAPI) — par IP ; désactiver pour tests intensifs : RATE_LIMIT_ENABLED=false
    rate_limit_enabled: bool = True
    rate_limit_default: str = "200/minute"
    rate_limit_login: str = "10/minute"

    model_config = {
        "env_file": str(_REPO_ROOT / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def postgres_utilisateur_url(self) -> str:
        return (
            f"postgresql://{self.postgres_utilisateur_user}:{self.postgres_utilisateur_password}"
            f"@{self.postgres_utilisateur_host}:{self.postgres_utilisateur_port}/{self.postgres_utilisateur_db}"
        )

    @property
    def postgres_sante_url(self) -> str:
        return (
            f"postgresql://{self.postgres_sante_user}:{self.postgres_sante_password}"
            f"@{self.postgres_sante_host}:{self.postgres_sante_port}/{self.postgres_sante_db}"
        )

    @property
    def postgres_gamification_url(self) -> str:
        return (
            f"postgresql://{self.postgres_gamification_user}:{self.postgres_gamification_password}"
            f"@{self.postgres_gamification_host}:{self.postgres_gamification_port}/{self.postgres_gamification_db}"
        )

    @property
    def mongodb_logs_url(self) -> str:
        return f"mongodb://{self.mongodb_logs_host}:{self.mongodb_logs_port}"

    @property
    def mongodb_reco_url(self) -> str:
        return f"mongodb://{self.mongodb_reco_host}:{self.mongodb_reco_port}"


settings = Settings()
