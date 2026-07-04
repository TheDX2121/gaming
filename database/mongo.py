from __future__ import annotations

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from shared.settings import Settings

_client: MongoClient | None = None
_db: Database | None = None


def get_db() -> Database:
    global _client, _db
    settings = Settings.load()
    if not settings.mongo_uri:
        raise RuntimeError("MONGO_URI is missing. Add it to your .env file.")
    if _db is None:
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=10000)
        _db = _client[settings.mongo_db_name]
        create_indexes(_db)
        seed_defaults(_db)
    return _db


def create_indexes(db: Database) -> None:
    db.users.create_index([("user_id", ASCENDING)], unique=True)
    db.active_games.create_index([("chat_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
    db.logs.create_index([("created_at", DESCENDING)])
    db.logs.create_index([("type", ASCENDING), ("created_at", DESCENDING)])
    db.transactions.create_index([("created_at", DESCENDING)])
    db.shop_items.create_index([("item_id", ASCENDING)], unique=True)
    db.matchmaking_queue.create_index([("game", ASCENDING), ("created_at", ASCENDING)])
    db.tournaments.create_index([("created_at", DESCENDING)])


def seed_defaults(db: Database) -> None:
    if not db.admin_treasury.find_one({"_id": "main"}):
        db.admin_treasury.insert_one({"_id": "main", "balance": 0, "total_shop_revenue": 0})

    default_items = [
        {"item_id": "hint_reveal", "name": "Reveal Letter", "price": 30, "category": "WordRiddle", "active": True, "description": "Reveal one letter in a WordRiddle hint."},
        {"item_id": "double_coins", "name": "Double Coins Boost", "price": 120, "category": "Boost", "active": True, "description": "Double game rewards for a limited time."},
        {"item_id": "roulette_shield", "name": "Roulette Shield", "price": 75, "category": "Game Perk", "active": True, "description": "Protect yourself once in Roulette."},
        {"item_id": "streak_protector", "name": "Streak Protector", "price": 90, "category": "Daily", "active": True, "description": "Protect daily streak once."},
        {"item_id": "vip_badge", "name": "VIP Badge", "price": 1000, "category": "Premium", "active": True, "description": "A rare profile badge."},
    ]
    for item in default_items:
        db.shop_items.update_one({"item_id": item["item_id"]}, {"$setOnInsert": item}, upsert=True)
