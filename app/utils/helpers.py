import sqlite3
from datetime import datetime, timedelta
from collections import Counter

# === Journal + Archetype Helpers ===
def sample_helper():
    return "This is a helper function."

def init_journal_db(db_path="custom_archetypes.db"):
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                entry_text TEXT,
                mood TEXT,
                energy_level TEXT,
                archetype TEXT,
                tags TEXT
            )
        ''')
        conn.commit()

def init_archetype_db(db_path="custom_archetypes.db"):
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS archetypes (
                name TEXT PRIMARY KEY,
                tone TEXT,
                template TEXT,
                traits TEXT,
                tags TEXT,
                created_at TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS archetype_versions (
                version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                archetype_name TEXT,
                tone TEXT,
                template TEXT,
                traits TEXT,
                tags TEXT,
                version_label TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()

def log_archetype_use(user_id, archetype, is_custom, module, mood, db_path="custom_archetypes.db"):
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS archetype_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                archetype TEXT,
                is_custom INTEGER,
                module TEXT,
                mood TEXT,
                timestamp TEXT
            )
        ''')
        conn.execute('''
            INSERT INTO archetype_usage (user_id, archetype, is_custom, module, mood, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, archetype, int(is_custom), module, mood, datetime.now().isoformat()))
        conn.commit()

def get_archetype_usage_summary(user_id, db_path="custom_archetypes.db"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT archetype, COUNT(*) FROM archetype_usage
            WHERE user_id = ?
            GROUP BY archetype
        ''', (user_id,))
        return cursor.fetchall()

def get_mood_archetype_matrix(user_id, db_path="custom_archetypes.db"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mood, archetype, COUNT(*) FROM archetype_usage
            WHERE user_id = ?
            GROUP BY mood, archetype
        ''', (user_id,))
        return cursor.fetchall()

# 💫 Emotion-Adaptive Helpers
def get_recent_mood_summary(user_id, db_path="custom_archetypes.db", lookback_days=3, top_n=1):
    cutoff = datetime.now() - timedelta(days=lookback_days)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mood FROM journal_entries
            WHERE user_id = ? AND date >= ?
        ''', (user_id, cutoff.isoformat()))
        moods = [row[0] for row in cursor.fetchall() if row[0]]
    mood_counts = Counter(moods)
    most_common = mood_counts.most_common(top_n)
    return [m[0] for m in most_common] if most_common else []

MOOD_ARCHETYPE_MAP = {
    "anxious":    {"archetype": "Orion",  "tone": "Soft, grounding, slow-paced"},
    "tired":      {"archetype": "Theo",   "tone": "Gentle, supportive, minimal"},
    "hopeful":    {"archetype": "Jasper", "tone": "Playful, poetic, inspiring"},
    "frustrated": {"archetype": "Beau",   "tone": "Reassuring, calm, validating"},
    "energetic":  {"archetype": "Fox",    "tone": "Witty, direct, high-tempo"},
    "foggy":      {"archetype": "Beau",   "tone": "Clear, affirming, structured"},
    "curious":    {"archetype": "Orion",  "tone": "Gentle, philosophical, open"},
    "focused":    {"archetype": "Theo",   "tone": "Minimal, direct, strategic"}
}

def map_mood_to_archetype(mood):
    mood = (mood or "").strip().lower()
    return MOOD_ARCHETYPE_MAP.get(mood, {"archetype": "Beau", "tone": "Warm, structured, validating"})

# Prompt Scaffold Helper
def get_prompt_scaffold(mode):
    """
    Returns a prompt scaffold string for a given mode.
    """
    scaffolds = {
        "planner": "Help the user create a clear, ADHD-friendly plan using encouraging and structured language.",
        "dopamenu": "Offer enjoyable micro-activities to gently boost dopamine and motivation.",
        "reflection": "Prompt the user to reflect on their emotional or mental state with warmth and insight.",
        "affirmation": "Deliver a gentle affirmation to support the user's self-worth and resilience.",
        "focus": "Encourage sustained attention through compassionate nudges and brief focus rituals."
    }
    return scaffolds.get(mode, "")

# Log Feedback Entry Helper (Updated to Accept db_path)
def log_feedback_entry(user_id, archetype, mood, input_text, response_text, rating, comment, db_path="custom_archetypes.db"):
    """
    Records user feedback after receiving a response from the assistant.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                archetype TEXT,
                mood TEXT,
                input TEXT,
                response TEXT,
                rating INTEGER,
                comment TEXT,
                timestamp TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO feedback (user_id, archetype, mood, input, response, rating, comment, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            archetype,
            mood,
            input_text,
            response_text,
            rating,
            comment,
            datetime.now().isoformat()
        ))
        conn.commit()
