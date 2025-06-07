from flask import Flask
from flask_cors import CORS
import logging

from src.extensions import db, login_manager, migrate
from src.models import User
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

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.login_view = 'main.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()

    # Register blueprints and logging
    setup_logging()
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7000, debug=True) 