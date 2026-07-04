from __future__ import annotations

from datetime import timedelta
from typing import Any

from database.mongo import get_db
from shared.time_utils import now_utc

STARTING_COINS = 100


def ensure_user(tg_user) -> dict[str, Any]:
    db = get_db()
    user_id = tg_user.id
    existing = db.users.find_one({"user_id": user_id})
    base = {
        "user_id": user_id,
        "username": tg_user.username,
        "first_name": tg_user.first_name,
        "last_name": tg_user.last_name,
        "coins": STARTING_COINS,
        "wins": 0,
        "losses": 0,
        "games_played": 0,
        "streak": 0,
        "last_daily": None,
        "inventory": {},
        "badges": [],
        "banned": False,
        "created_at": now_utc(),
        "updated_at": now_utc(),
    }
    if not existing:
        db.users.insert_one(base)
        log("user", "registered", user_id=user_id, details={"username": tg_user.username})
        return base
    db.users.update_one({"user_id": user_id}, {"$set": {"username": tg_user.username, "first_name": tg_user.first_name, "last_name": tg_user.last_name, "updated_at": now_utc()}})
    return db.users.find_one({"user_id": user_id})


def get_user(user_id: int) -> dict[str, Any] | None:
    return get_db().users.find_one({"user_id": user_id})


def is_banned(user_id: int) -> bool:
    user = get_user(user_id)
    return bool(user and user.get("banned"))


def add_coins(user_id: int, amount: int, reason: str = "game_reward") -> None:
    db = get_db()
    db.users.update_one({"user_id": user_id}, {"$inc": {"coins": amount}, "$set": {"updated_at": now_utc()}})
    db.transactions.insert_one({"type": "credit", "user_id": user_id, "amount": amount, "reason": reason, "created_at": now_utc()})
    log("coin", "add_coins", user_id=user_id, details={"amount": amount, "reason": reason})


def remove_coins(user_id: int, amount: int, reason: str = "manual_remove") -> bool:
    db = get_db()
    user = get_user(user_id)
    if not user or user.get("coins", 0) < amount:
        return False
    db.users.update_one({"user_id": user_id}, {"$inc": {"coins": -amount}, "$set": {"updated_at": now_utc()}})
    db.transactions.insert_one({"type": "debit", "user_id": user_id, "amount": amount, "reason": reason, "created_at": now_utc()})
    log("coin", "remove_coins", user_id=user_id, details={"amount": amount, "reason": reason})
    return True


def spend_to_treasury(user_id: int, amount: int, reason: str) -> bool:
    db = get_db()
    if not remove_coins(user_id, amount, reason=reason):
        return False
    db.admin_treasury.update_one({"_id": "main"}, {"$inc": {"balance": amount, "total_shop_revenue": amount}}, upsert=True)
    db.transactions.insert_one({"type": "treasury_credit", "user_id": user_id, "amount": amount, "reason": reason, "created_at": now_utc()})
    log("treasury", "user_spent_to_admin", user_id=user_id, details={"amount": amount, "reason": reason})
    return True


def record_game_result(user_id: int, game_id: str, won: bool, coins: int = 0) -> None:
    db = get_db()
    inc = {"games_played": 1, "wins" if won else "losses": 1}
    db.users.update_one({"user_id": user_id}, {"$inc": inc, "$set": {"updated_at": now_utc()}})
    if coins:
        add_coins(user_id, coins, reason=f"reward:{game_id}")
    log("game", "result", user_id=user_id, details={"game": game_id, "won": won, "coins": coins})


def claim_daily(user_id: int) -> tuple[bool, str]:
    db = get_db()
    user = get_user(user_id)
    if not user:
        return False, "User not found."
    now = now_utc()
    last = user.get("last_daily")
    if last and (now - last) < timedelta(hours=20):
        remaining = timedelta(hours=20) - (now - last)
        return False, f"Daily reward already claimed. Try again in about {int(remaining.total_seconds() // 3600)} hours."
    streak = int(user.get("streak", 0)) + 1
    reward = 50 + min(streak * 10, 200)
    db.users.update_one({"user_id": user_id}, {"$set": {"last_daily": now, "streak": streak}, "$inc": {"coins": reward}})
    log("coin", "daily_claim", user_id=user_id, details={"reward": reward, "streak": streak})
    return True, f"🎁 Daily reward claimed! +{reward} coins. Streak: {streak} days."


def start_active_game(chat_id: int, user_id: int, game_id: str, state: dict[str, Any]) -> None:
    get_db().active_games.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"chat_id": chat_id, "user_id": user_id, "game_id": game_id, "state": state, "created_at": now_utc(), "updated_at": now_utc()}},
        upsert=True,
    )


def get_active_game(chat_id: int, user_id: int) -> dict[str, Any] | None:
    return get_db().active_games.find_one({"chat_id": chat_id, "user_id": user_id})


def clear_active_game(chat_id: int, user_id: int) -> None:
    get_db().active_games.delete_one({"chat_id": chat_id, "user_id": user_id})


def update_active_state(chat_id: int, user_id: int, state: dict[str, Any]) -> None:
    get_db().active_games.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"state": state, "updated_at": now_utc()}})


def log(type_: str, action: str, user_id: int | None = None, details: dict[str, Any] | None = None) -> None:
    get_db().logs.insert_one({
        "type": type_,
        "action": action,
        "user_id": user_id,
        "details": details or {},
        "created_at": now_utc(),
    })


def get_top(limit: int = 10) -> list[dict[str, Any]]:
    return list(get_db().users.find({"banned": {"$ne": True}}).sort("coins", -1).limit(limit))


def get_shop_items(category: str | None = None) -> list[dict[str, Any]]:
    q: dict[str, Any] = {"active": True}
    if category:
        q["category"] = category
    return list(get_db().shop_items.find(q).sort("price", 1))


def buy_item(user_id: int, item_id: str) -> tuple[bool, str]:
    db = get_db()
    item = db.shop_items.find_one({"item_id": item_id, "active": True})
    if not item:
        return False, "Item not found."
    price = int(item.get("price", 0))
    if not spend_to_treasury(user_id, price, reason=f"shop:{item_id}"):
        return False, "Not enough coins."
    db.users.update_one({"user_id": user_id}, {"$inc": {f"inventory.{item_id}": 1}})
    db.transactions.insert_one({"type": "purchase", "user_id": user_id, "item_id": item_id, "amount": price, "created_at": now_utc()})
    log("shop", "purchase", user_id=user_id, details={"item_id": item_id, "price": price})
    return True, f"✅ Purchased {item.get('name')} for {price} coins."


def use_inventory_item(user_id: int, item_id: str) -> bool:
    db = get_db()
    user = get_user(user_id)
    if not user or user.get("inventory", {}).get(item_id, 0) <= 0:
        return False
    db.users.update_one({"user_id": user_id}, {"$inc": {f"inventory.{item_id}": -1}})
    log("shop", "use_item", user_id=user_id, details={"item_id": item_id})
    return True
