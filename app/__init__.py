from flask import Flask
from .config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register the blueprint from routes.py
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app

