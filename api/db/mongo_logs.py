from pymongo import MongoClient
from api.config import settings

_client_logs: MongoClient | None = None


def get_mongo_logs() -> MongoClient:
    global _client_logs
    if _client_logs is None:
        _client_logs = MongoClient(settings.mongodb_logs_url)
    return _client_logs[settings.mongodb_logs_db]
