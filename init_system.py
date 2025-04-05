import os
from app.utils.helpers import init_journal_db, init_archetype_db

# Create required directories if they don't exist
required_dirs = [
    "uploads",
    "exports",
    "app/static/audio"
]

for directory in required_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")
    else:
        print(f"✅ Directory exists: {directory}")

# Initialize SQLite databases and tables
print("\n🧠 Initializing journal + archetype tables...")
try:
    init_journal_db()
    init_archetype_db()
    print("✅ Database tables ready.")
except Exception as e:
    print(f"❌ Failed to initialize DB tables: {e}")