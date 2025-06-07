from flask import Flask
from flask_cors import CORS
import logging
from src.routes.main import main_blueprint

def setup_logging():
    # Configure general logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/logs.txt"),
            logging.StreamHandler()
        ]
    )
    # Configure chat logging
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
    
    setup_logging()
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7000, debug=True) 