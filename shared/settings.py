import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Settings:
    bot_token: str
    mongo_uri: str
    mongo_db_name: str
    admin_username: str
    admin_password: str
    flask_host: str
    flask_port: int
    flask_debug: bool
    secret_key: str | None = None

    @staticmethod
    def load() -> "Settings":
        load_dotenv()
        return Settings(
            bot_token=os.getenv("BOT_TOKEN", "").strip(),
            mongo_uri=os.getenv("MONGO_URI", "").strip(),
            mongo_db_name=os.getenv("MONGO_DB_NAME", "telegram_gaming_bot").strip(),
            admin_username=os.getenv("ADMIN_USERNAME", "admin").strip(),
            admin_password=os.getenv("ADMIN_PASSWORD", "admin123").strip(),
            flask_host=os.getenv("FLASK_HOST", "127.0.0.1").strip(),
            flask_port=int(os.getenv("FLASK_PORT", "5000")),
            flask_debug=os.getenv("FLASK_DEBUG", "True").lower() == "true",
            secret_key=os.getenv("SECRET_KEY"),
        )
