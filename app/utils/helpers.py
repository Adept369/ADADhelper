"""
app/utils/helpers.py

This module contains helper functions for:
  - Initializing the SQLite database tables.
  - Logging archetype usage and user feedback.
  - Retrieving recent mood summaries.
  - Mapping moods to archetypes.
  - Providing preset prompt scaffolds.
"""

import sqlite3
from datetime import datetime, timedelta
from collections import Counter

def init_journal_db(db_path="custom_archetypes.db"):
    """
    Initializes the journal_entries table in the SQLite database.

    Args:
        db_path (str): Path to the SQLite database file.
    """
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
    """
    Initializes the archetypes and archetype_versions tables in the SQLite database.

    Args:
        db_path (str): Path to the SQLite database file.
    """
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
    """
    Logs the usage of an archetype by a user.

    Args:
        user_id (str): The ID of the user.
        archetype (str): The archetype used.
        is_custom (bool): True if the archetype is custom.
        module (str): The module (endpoint) where the archetype was used.
        mood (str): The mood associated with the usage.
        db_path (str): Path to the SQLite database file.
    """
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
    """
    Retrieves a summary of archetype usage for a given user.

    Args:
        user_id (str): The user ID to filter by.
        db_path (str): Path to the SQLite database file.

    Returns:
        list: A list of tuples (archetype, count) representing usage counts.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT archetype, COUNT(*) FROM archetype_usage
            WHERE user_id = ?
            GROUP BY archetype
        ''', (user_id,))
        return cursor.fetchall()

def get_mood_archetype_matrix(user_id, db_path="custom_archetypes.db"):
    """
    Retrieves a matrix of mood and archetype combinations with usage counts for a given user.

    Args:
        user_id (str): The user ID to filter by.
        db_path (str): Path to the SQLite database file.

    Returns:
        list: A list of tuples (mood, archetype, count).
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mood, archetype, COUNT(*) FROM archetype_usage
            WHERE user_id = ?
            GROUP BY mood, archetype
        ''', (user_id,))
        return cursor.fetchall()

def get_recent_mood_summary(user_id, db_path="custom_archetypes.db", lookback_days=3, top_n=1):
    """
    Retrieves the most common recent moods for a user within a specified lookback period.

    Args:
        user_id (str): The ID of the user.
        db_path (str): Path to the SQLite database file.
        lookback_days (int): Number of days to look back.
        top_n (int): Number of top moods to return.

    Returns:
        list: A list of moods, sorted by frequency.
    """
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
    """
    Maps a given mood to a corresponding archetype and tone.

    Args:
        mood (str): The mood to map.

    Returns:
        dict: A dictionary with keys 'archetype' and 'tone'. Defaults to Beau if not found.
    """
    mood = (mood or "").strip().lower()
    return MOOD_ARCHETYPE_MAP.get(mood, {"archetype": "Beau", "tone": "Warm, structured, validating"})

def get_prompt_scaffold(mode):
    """
    Returns a prompt scaffold string for a given mode.

    Args:
        mode (str): The mode for which to get the prompt scaffold.

    Returns:
        str: A prompt scaffold string. Returns an empty string if the mode is not recognized.
    """
    scaffolds = {
        "planner": "Help the user create a clear, ADHD-friendly plan using encouraging and structured language.",
        "dopamenu": "Offer enjoyable micro-activities to gently boost dopamine and motivation.",
        "reflection": "Prompt the user to reflect on their emotional or mental state with warmth and insight.",
        "affirmation": "Deliver a gentle affirmation to support the user's self-worth and resilience.",
        "focus": "Encourage sustained attention through compassionate nudges and brief focus rituals."
    }
    return scaffolds.get(mode, "")

def log_feedback_entry(user_id, archetype, mood, input_text, response_text, rating, comment, db_path="custom_archetypes.db"):
    """
    Records user feedback after receiving a response from the assistant.

    Args:
        user_id (str): The ID of the user providing feedback.
        archetype (str): The archetype used for the response.
        mood (str): The user's mood at the time of the response.
        input_text (str): The input prompt provided by the user.
        response_text (str): The response generated by the assistant.
        rating (int): A rating on a scale of 1 to 5.
        comment (str): Optional text feedback.
        db_path (str): Path to the SQLite database file.
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
