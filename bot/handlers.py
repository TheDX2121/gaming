from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.catalog import GAME_CATEGORIES, GAMES
from bot.keyboards import main_games_keyboard, category_keyboard, game_keyboard, shop_keyboard, buy_keyboard
from bot import services
from bot.games import start_game, handle_rps, handle_reaction, handle_ttt


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = services.ensure_user(update.effective_user)
    if user.get("banned"):
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    await update.message.reply_text(
        "🎮 Welcome to the Advanced Gaming Bot!\n\nUse /games to open the game hub.",
        reply_markup=main_games_keyboard(),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Commands:\n"
        "/start - start bot\n"
        "/games - open inline game hub\n"
        "/profile - view coins and stats\n"
        "/daily - claim daily reward\n"
        "/top - leaderboard\n"
        "/help - help\n\n"
        "Most games are played with buttons, not commands."
    )


async def games_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services.ensure_user(update.effective_user)
    await update.message.reply_text("🎮 GAME HUB\nChoose a section:", reply_markup=main_games_keyboard())


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = services.ensure_user(update.effective_user)
    inv = user.get("inventory", {})
    inv_text = ", ".join(f"{k}×{v}" for k, v in inv.items() if v > 0) or "Empty"
    await update.message.reply_text(
        f"👤 Profile\n"
        f"Name: {user.get('first_name') or 'Player'}\n"
        f"Coins: {user.get('coins', 0)}\n"
        f"Wins: {user.get('wins', 0)}\n"
        f"Losses: {user.get('losses', 0)}\n"
        f"Games Played: {user.get('games_played', 0)}\n"
        f"Streak: {user.get('streak', 0)}\n"
        f"Inventory: {inv_text}"
    )


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services.ensure_user(update.effective_user)
    ok, msg = services.claim_daily(update.effective_user.id)
    await update.message.reply_text(msg)


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    users = services.get_top(10)
    lines = ["🏆 Leaderboard"]
    for i, u in enumerate(users, 1):
        name = u.get("username") or u.get("first_name") or str(u.get("user_id"))
        lines.append(f"{i}. {name} — {u.get('coins', 0)} coins")
    await update.message.reply_text("\n".join(lines))


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    services.ensure_user(q.from_user)
    data = q.data or ""

    if data == "home":
        await q.edit_message_text("🎮 GAME HUB\nChoose a section:", reply_markup=main_games_keyboard())
        return

    if data.startswith("cat:"):
        cat = data.split(":", 1)[1]
        await q.edit_message_text(GAME_CATEGORIES[cat]["title"], reply_markup=category_keyboard(cat))
        return

    if data.startswith("game:"):
        game_id = data.split(":", 1)[1]
        await q.edit_message_text(f"{GAMES[game_id]['name']}\n\nChoose an option:", reply_markup=game_keyboard(game_id))
        return

    if data.startswith("help:"):
        key = data.split(":", 1)[1]
        if key == "global":
            await q.edit_message_text(
                "❓ How to Play\n\n"
                "1. Use /games.\n"
                "2. Choose a category.\n"
                "3. Open a game.\n"
                "4. Tap Play.\n"
                "5. Some games use buttons, some ask you to type an answer.\n\n"
                "Coins are earned by playing. Spend them in Shop.",
                reply_markup=main_games_keyboard(),
            )
        else:
            await q.edit_message_text(f"{GAMES[key]['name']} - How to Play\n\n{GAMES[key]['help']}", reply_markup=game_keyboard(key))
        return

    if data.startswith("cathelp:"):
        cat = data.split(":", 1)[1]
        await q.edit_message_text(f"❓ {GAME_CATEGORIES[cat]['title']} Help\n\nChoose any game, read its How to Play, then tap Play.", reply_markup=category_keyboard(cat))
        return

    if data.startswith("play:"):
        game_id = data.split(":", 1)[1]
        await start_game(update, context, game_id)
        return

    if data == "leaderboard":
        users = services.get_top(10)
        lines = ["🏆 Leaderboard"]
        for i, u in enumerate(users, 1):
            name = u.get("username") or u.get("first_name") or str(u.get("user_id"))
            lines.append(f"{i}. {name} — {u.get('coins', 0)} coins")
        await q.edit_message_text("\n".join(lines), reply_markup=main_games_keyboard())
        return

    if data == "shop:home":
        user = services.get_user(q.from_user.id) or {}
        await q.edit_message_text(f"🛒 SHOP\nYour Coins: {user.get('coins', 0)}\nChoose a section:", reply_markup=shop_keyboard())
        return

    if data == "shop:help":
        await q.edit_message_text("🛒 Shop Help\n\nBuy items with coins. Every coin spent goes into Admin Treasury and is logged.", reply_markup=shop_keyboard())
        return

    if data.startswith("shopcat:"):
        category = data.split(":", 1)[1]
        items = services.get_shop_items(category)
        if not items:
            await q.edit_message_text("No items in this shop category.", reply_markup=shop_keyboard())
            return
        text = f"🛒 {category} Items\n\n"
        rows = []
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        for item in items:
            text += f"• {item['name']} — {item['price']} coins\n  {item.get('description', '')}\n"
            rows.append([InlineKeyboardButton(f"Buy {item['name']} ({item['price']})", callback_data=f"item:{item['item_id']}")])
        rows.append([InlineKeyboardButton("⬅️ Back", callback_data="shop:home")])
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows))
        return

    if data.startswith("item:"):
        item_id = data.split(":", 1)[1]
        items = [i for i in services.get_shop_items() if i["item_id"] == item_id]
        if not items:
            await q.edit_message_text("Item not found.", reply_markup=shop_keyboard())
            return
        item = items[0]
        await q.edit_message_text(f"{item['name']}\nPrice: {item['price']} coins\n\n{item.get('description','')}", reply_markup=buy_keyboard(item_id))
        return

    if data.startswith("buy:"):
        item_id = data.split(":", 1)[1]
        ok, msg = services.buy_item(q.from_user.id, item_id)
        await q.edit_message_text(msg, reply_markup=shop_keyboard())
        return

    if data.startswith("rps:"):
        await handle_rps(update, context, data.split(":", 1)[1])
        return

    if data == "react:tap":
        await handle_reaction(update, context)
        return

    if data.startswith("ttt:"):
        await handle_ttt(update, context, int(data.split(":", 1)[1]))
        return

    await q.edit_message_text("Unknown button action.")
