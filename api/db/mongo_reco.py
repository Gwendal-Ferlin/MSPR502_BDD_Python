from pymongo import MongoClient
from api.config import settings

_client_reco: MongoClient | None = None


def get_mongo_reco() -> MongoClient:
    global _client_reco
    if _client_reco is None:
        _client_reco = MongoClient(settings.mongodb_reco_url)
    return _client_reco[settings.mongodb_reco_db]
