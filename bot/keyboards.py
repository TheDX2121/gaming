from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.catalog import GAME_CATEGORIES, GAMES


def main_games_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Luck Games", callback_data="cat:luck"), InlineKeyboardButton("🧠 Word Games", callback_data="cat:word")],
        [InlineKeyboardButton("⚔️ Competitive", callback_data="cat:competitive"), InlineKeyboardButton("🎭 Fun Group Games", callback_data="cat:fun")],
        [InlineKeyboardButton("👥 Multiplayer", callback_data="cat:multi"), InlineKeyboardButton("🛒 Shop", callback_data="shop:home")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"), InlineKeyboardButton("❓ How to Play", callback_data="help:global")],
    ])


def category_keyboard(category_id: str) -> InlineKeyboardMarkup:
    games = GAME_CATEGORIES[category_id]["games"]
    rows = []
    for i in range(0, len(games), 2):
        row = []
        for game_id in games[i:i+2]:
            row.append(InlineKeyboardButton(GAMES[game_id]["name"], callback_data=f"game:{game_id}"))
        rows.append(row)
    rows.append([InlineKeyboardButton("❓ How to Play", callback_data=f"cathelp:{category_id}"), InlineKeyboardButton("⬅️ Back", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def game_keyboard(game_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Play", callback_data=f"play:{game_id}"), InlineKeyboardButton("❓ How to Play", callback_data=f"help:{game_id}")],
        [InlineKeyboardButton("⬅️ Back to Games", callback_data="home")],
    ])


def shop_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Boosts", callback_data="shopcat:Boost"), InlineKeyboardButton("🧩 WordRiddle Items", callback_data="shopcat:WordRiddle")],
        [InlineKeyboardButton("🎮 Game Perks", callback_data="shopcat:Game Perk"), InlineKeyboardButton("🎁 Daily", callback_data="shopcat:Daily")],
        [InlineKeyboardButton("🏆 Premium", callback_data="shopcat:Premium"), InlineKeyboardButton("❓ How Shop Works", callback_data="shop:help")],
        [InlineKeyboardButton("⬅️ Back", callback_data="home")],
    ])


def buy_keyboard(item_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Buy", callback_data=f"buy:{item_id}"), InlineKeyboardButton("❌ Cancel", callback_data="shop:home")]
    ])


def rps_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✊ Rock", callback_data="rps:rock"), InlineKeyboardButton("📄 Paper", callback_data="rps:paper"), InlineKeyboardButton("✂️ Scissors", callback_data="rps:scissors")],
        [InlineKeyboardButton("⬅️ Back", callback_data="home")],
    ])


def reaction_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⚡ TAP NOW", callback_data="react:tap")]])


def tic_tac_toe_keyboard(board: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, 9, 3):
        rows.append([
            InlineKeyboardButton(board[i] if board[i] != " " else "·", callback_data=f"ttt:{i}"),
            InlineKeyboardButton(board[i+1] if board[i+1] != " " else "·", callback_data=f"ttt:{i+1}"),
            InlineKeyboardButton(board[i+2] if board[i+2] != " " else "·", callback_data=f"ttt:{i+2}"),
        ])
    return InlineKeyboardMarkup(rows)
