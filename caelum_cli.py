# caelum_cli.py
import sqlite3
from app.llm import LLMEngine
from app.utils.helpers import get_recent_mood_summary, map_mood_to_archetype

def load_archetype_prompt(archetype: str):
    conn = sqlite3.connect("custom_archetypes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT tone, template FROM archetypes WHERE name = ?", (archetype,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Warm, structured", "[Beau Mode]\nGently respond."
    return row[0], row[1]

def auto_detect_archetype(user_id="anonymous"):
    moods = get_recent_mood_summary(user_id, top_n=1)
    if not moods:
        print("🕯️ No recent mood logs. Defaulting to Beau.")
        return "Beau"
    result = map_mood_to_archetype(moods[0])
    print(f"🔍 Latest mood: {moods[0]} → Archetype: {result['archetype']}")
    return result["archetype"]

def main():
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
