# caelum_cli.py
"""
Caelum CLI — A command-line interface for testing the Caelum AI Assistant.
This script allows you to interact with the LLM using a selected archetype,
with options for auto-detection based on recent mood logs.
"""

import sqlite3
from app.llm import LLMEngine
from app.utils.helpers import get_recent_mood_summary, map_mood_to_archetype

def load_archetype_prompt(archetype: str):
    """
    Retrieve the tone and template for a given archetype from the database.
    Returns:
        tuple: (tone, template) for the archetype or default values if not found.
    """
    with sqlite3.connect("custom_archetypes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tone, template FROM archetypes WHERE name = ?", (archetype,))
        row = cursor.fetchone()
    if not row:
        return "Warm, structured", "[Beau Mode]\nGently respond."
    return row[0], row[1]

def auto_detect_archetype(user_id="anonymous"):
    """
    Auto-detect the archetype based on recent mood entries.
    Returns:
        str: The detected archetype, or "Beau" if no mood data is available.
    """
    moods = get_recent_mood_summary(user_id, top_n=1)
    if not moods:
        print("🕯️ No recent mood logs. Defaulting to Beau.")
        return "Beau"
    result = map_mood_to_archetype(moods[0])
    print(f"🔍 Latest mood: {moods[0]} → Archetype: {result['archetype']}")
    return result["archetype"]

def main():
    """
    Main function to run the Caelum CLI.
    Prompts the user for input and outputs the response from the LLM.
    """
    llm = LLMEngine()
    print("🧠 Caelum CLI is ready for development testing.")
    
    user_id = input("🆔 Enter user_id (default = anonymous): ").strip() or "anonymous"
    use_auto = input("🤖 Auto-detect archetype from recent mood? (y/n): ").lower().strip() == "y"
    
    if use_auto:
        archetype = auto_detect_archetype(user_id)
    else:
        archetype = input("🎭 Enter archetype name (default = Beau): ").strip() or "Beau"

    tone, template = load_archetype_prompt(archetype)

    print(f"\n🎨 Archetype: {archetype}\n🗣️ Tone: {tone}\n📜 Template:\n{template}")
    print("\nBegin typing your prompt below (Ctrl+C to exit):")

    while True:
        try:
            user_input = input("\n🗣️ You: ")
            if not user_input.strip():
                continue
            response = llm.generate_archetype_prompt(user_input, tone, template, archetype)
            print(f"\n🤖 Caelum ({archetype}): {response}")
        except KeyboardInterrupt:
            print("\n👋 Exiting Caelum CLI.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
