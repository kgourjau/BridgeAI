from flask import Flask
from flask_cors import CORS
import logging
import os
from src.routes.main import main_blueprint

def setup_logging(app):
    # Ensure log directory exists for chat logs
    os.makedirs("logs", exist_ok=True)

    # Remove any default handlers that Flask might have added
    app.logger.handlers.clear()
    
    # Integrate with Gunicorn's logger if running under Gunicorn
    if 'gunicorn' in os.environ.get('SERVER_SOFTWARE', ''):
        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers.extend(gunicorn_error_logger.handlers)
        app.logger.setLevel(gunicorn_error_logger.level)
    else:
        # For local development, log to the console
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    # Configure dedicated chat logging to a file
    chat_logger = logging.getLogger("chat_logger")
    chat_logger.setLevel(logging.INFO)
    chat_formatter = logging.Formatter('%(asctime)s - %(message)s')
    chat_handler = logging.FileHandler("logs/chat_logs.txt")
    chat_handler.setFormatter(chat_formatter)
    chat_logger.addHandler(chat_handler)
    chat_logger.propagate = False

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('src/config.py')

    CORS(app)
    
    setup_logging(app)
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7000, debug=True) 