import os
from web_panel.app import create_app
from shared.settings import Settings

if __name__ == "__main__":
    settings = Settings.load()
    app = create_app()

    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))

    app.run(
        host=host,
        port=port,
        debug=settings.flask_debug,
    )
