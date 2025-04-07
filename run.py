"""
run.py - Entry point for the Caelum ADHD Assistant Flask application.
Loads environment variables and creates the Flask app via the factory.
"""

from dotenv import load_dotenv
import os
from app import create_app
import logging

# Load environment variables from .env file
load_dotenv()

# Optionally select configuration based on an environment variable
config_class = os.getenv("FLASK_CONFIG", "app.config.DevelopmentConfig")
app = create_app(config_class=config_class)

# Configure logging (optional, but useful)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting Caelum ADHD Assistant...")

if __name__ == "__main__":
    # Run the Flask development server.
    # For production, use a WSGI server like Gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=(config_class == "app.config.DevelopmentConfig"))
