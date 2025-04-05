from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from flask import Flask
from .config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register routes blueprint
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app


