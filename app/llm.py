import os
import openai
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.config import Config

# === Setup Keys & Paths ===
if not openai.api_key:
    openai.api_key = Config.OPENAI_API_KEY

ELEVENLABS_API_KEY = Config.ELEVENLABS_API_KEY
AUDIO_OUTPUT_DIR = Path(Config.AUDIO_OUTPUT_DIR)
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
VOICE_MAP = Config.VOICE_MAP

class LLMEngine:
    def __init__(self, model="gpt-4", debug=True):
        self.model = model
        self.debug = debug
        if not openai.api_key:
            openai.api_key = Config.OPENAI_API_KEY
        if not openai.api_key:
            raise Exception("OPENAI_API_KEY is not set.")

    def generate_response(self, prompt: str, system_msg: str = "You are a helpful assistant.") -> str:
        if self.debug:
            print(f"[DEBUG] Generating response: {prompt}", flush=True)
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.85,
                max_tokens=500
            )
            return response.choices[0]['message']['content']
        except Exception as e:
            print(f"[DEBUG] Error generating response: {e}", flush=True)
            raise

    def generate_archetype_prompt(self, user_input: str, tone: str, template: str, archetype: str) -> str:
        messages = [
            {"role": "system", "content": f"You are Caelum Wren in {archetype} mode. Tone: {tone}"},
            {"role": "user", "content": f"{template}\nUser input: \"{user_input}\""}
        ]
        if self.debug:
            print(f"[DEBUG] Archetype Prompt: {messages}", flush=True)
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.85,
                max_tokens=500
            )
            return response.choices[0]['message']['content']
        except Exception as e:
            print(f"[DEBUG] Error in archetype prompt: {e}", flush=True)
            raise

    def transcribe_audio_whisper(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as audio_file:
                result = openai.Audio.transcribe("whisper-1", audio_file)
            return result["text"]
        except Exception as e:
            print(f"[DEBUG] Whisper transcription error: {e}", flush=True)
            raise

    def generate_tts_elevenlabs(self, text: str, archetype: str = "Beau") -> str:
        voice_id = VOICE_MAP.get(archetype, VOICE_MAP["Beau"])
        output_file = AUDIO_OUTPUT_DIR / f"{archetype}_{datetime.now().timestamp()}.mp3"

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                with open(output_file, "wb") as f:
                    f.write(response.content)
                return str(output_file)
            else:
                raise Exception(f"ElevenLabs API failed: {response.status_code} – {response.text}")
        except Exception as e:
            print(f"[DEBUG] ElevenLabs TTS error: {e}", flush=True)
            raise

    def set_voice_map(self, new_map: dict):
        global VOICE_MAP
        VOICE_MAP.update(new_map)
        if self.debug:
            print(f"[DEBUG] Voice map updated: {VOICE_MAP}", flush=True)
