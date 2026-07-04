from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from shared.settings import Settings
from database.mongo import get_db
from bot.handlers import start, help_cmd, games_cmd, profile, daily, top, callback_handler
from bot.games import handle_text_answer


def run_bot() -> None:
    settings = Settings.load()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is missing. Add it to .env")
    get_db()  # initialize database and default shop items

    app = ApplicationBuilder().token(settings.bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("games", games_cmd))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_answer))

    print("Gaming bot is running...")
    app.run_polling(allowed_updates=["message", "callback_query"])
