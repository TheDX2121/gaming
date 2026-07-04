import os
import threading

from bot.main import run_bot
from web_panel.app import create_app
from shared.settings import Settings


def start_web_panel():
    settings = Settings.load()
    app = create_app()

    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))

    app.run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    web_thread = threading.Thread(target=start_web_panel, daemon=True)
    web_thread.start()

    run_bot()
