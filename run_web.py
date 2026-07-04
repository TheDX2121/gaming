from web_panel.app import create_app
from shared.settings import Settings

if __name__ == "__main__":
    settings = Settings.load()
    app = create_app()
    app.run(host=settings.flask_host, port=settings.flask_port, debug=settings.flask_debug)
