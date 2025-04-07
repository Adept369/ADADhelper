"""
init_system.py

This script initializes the required directory structure and SQLite databases
for the Caelum ADHD Assistant. It ensures that directories for uploads, exports,
and static audio files exist and then calls functions to initialize the journal
and archetype databases.
"""

import os
import logging
from app.utils.helpers import init_journal_db, init_archetype_db

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# List of directories required for the application
REQUIRED_DIRS = [
    "uploads",
    "exports",
    "app/static/audio"
]

def create_directories():
    """Ensure all required directories exist."""
    for directory in REQUIRED_DIRS:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logging.info(f"📁 Created directory: {directory}")
            else:
                logging.info(f"✅ Directory exists: {directory}")
        except Exception as e:
            logging.error(f"❌ Error creating directory {directory}: {e}")

def initialize_databases():
    """Initialize SQLite databases and tables."""
    logging.info("🧠 Initializing journal + archetype tables...")
    try:
        init_journal_db()
        init_archetype_db()
        logging.info("✅ Database tables ready.")
    except Exception as e:
        logging.error(f"❌ Failed to initialize DB tables: {e}")

def main():
    """Main function to set up directories and initialize databases."""
    create_directories()
    initialize_databases()

if __name__ == "__main__":
    main()
