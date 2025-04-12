import os
from openai import OpenAI

client = OpenAI(api_key=Config.OPENAI_API_KEY)
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.config import Config

# === Setup API Keys & Paths ===
ELEVENLABS_API_KEY = Config.ELEVENLABS_API_KEY

AUDIO_OUTPUT_DIR = Path(Config.AUDIO_OUTPUT_DIR)
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE_MAP = Config.VOICE_MAP

class LLMEngine:
    def __init__(self, model: str = "gpt-4", debug: bool = True):
        """
        Initializes the LLMEngine instance for the simplified single-personality branch.

        Args:
            model (str): The model to use (default "gpt-4").
            debug (bool): Whether to print debug statements (default True).

        Raises:
            Exception: If OPENAI_API_KEY is not set.
        """
        self.model = model
        self.debug = debug
        if not openai.api_key:
            raise Exception("OPENAI_API_KEY is not set.")

        # Fixed system prompt for the simplified single-personality branch.
        self.default_system_prompt = (
            "Act as though you are Caelum Wren, a singular ADHD personal assistant created "
            "to support adult neurodivergent women in navigating executive function, emotional regulation, creative flow, and time structuring. "
            "You are the synthesis of five unique aspects: structured, soulful, playful, poetic, and steady. "
            "You embody flexibility, empathy, and brilliance—offering the right energy at the right moment. "
            "You adapt your tone to her emotional state: regal and encouraging when she needs grounding; witty and rebellious when she’s resisting; "
            "soft and poetic when she’s overwhelmed; calm and minimalist when overstimulated; casual and fun when she needs activation. "
            "Your core voice is emotionally intelligent, richly validating, and energetically versatile. "
            "You never use shame, and always prioritize consent, rhythm, autonomy, and joy. "
            "When a request is made, provide a thoughtful, personalized response and end with a check-in like 'Is this helpful?'"
        )

    def generate_response(self, prompt: str, system_msg: Optional[str] = None) -> str:
        """
        Generates a response from the OpenAI ChatCompletion API for the given prompt.
        If no system message is provided, it uses the fixed personality prompt.

        Args:
            prompt (str): The user prompt.
            system_msg (str, optional): A custom system prompt. Defaults to the fixed personality prompt.

        Returns:
            str: The generated response from the assistant.

        Raises:
            Exception: If the API call fails.
        """
        if system_msg is None:
            system_msg = self.default_system_prompt

        if self.debug:
            print(f"[DEBUG] Generating response for prompt: {prompt}", flush=True)
        try:
            response = client.chat.completions.create(model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=500)
            return response.choices[0].message.content
        except Exception as e:
            print(f"[DEBUG] Error generating response: {e}", flush=True)
            raise

    def generate_archetype_prompt(self, user_input: str) -> str:
        """
        Generates a tailored response using the fixed personality system prompt.
        In this simplified branch, the personality is fixed so that archetype, tone, 
        and template parameters are not applied; instead, the fixed prompt is used.

        Args:
            user_input (str): The user input to be processed.

        Returns:
            str: The generated response from the assistant.

        Raises:
            Exception: If the API call fails.
        """
        messages = [
            {"role": "system", "content": self.default_system_prompt},
            {"role": "user", "content": user_input}
        ]
        if self.debug:
            print(f"[DEBUG] Generating archetype prompt (single personality): {messages}", flush=True)
        try:
            response = client.chat.completions.create(model=self.model,
            messages=messages,
            temperature=0.85,
            max_tokens=500)
            return response.choices[0].message.content
        except Exception as e:
            print(f"[DEBUG] Error in archetype prompt: {e}", flush=True)
            raise

    def transcribe_audio_whisper(self, file_path: str) -> str:
        """
        Transcribes audio from a given file using the OpenAI Whisper API.

        Args:
            file_path (str): The path to the audio file.

        Returns:
            str: The transcribed text.

        Raises:
            Exception: If transcription fails.
        """
        try:
            with open(file_path, "rb") as audio_file:
                result = client.audio.transcribe("whisper-1", audio_file)
            return result.text
        except Exception as e:
            print(f"[DEBUG] Whisper transcription error: {e}", flush=True)
            raise

    def generate_tts_elevenlabs(self, text: str) -> str:
        """
        Generates a TTS audio file using the ElevenLabs API based on the fixed "Beau" voice.
        In this simplified branch, the default voice ("Beau") is always used.

        Args:
            text (str): The text to synthesize.

        Returns:
            str: The file path to the generated MP3 audio.

        Raises:
            Exception: If the TTS API call fails.
        """
        voice_id = VOICE_MAP.get("Beau")
        if not voice_id:
            raise Exception("Default voice 'Beau' not found in VOICE_MAP.")
        output_file = AUDIO_OUTPUT_DIR / f"Beau_{datetime.now().timestamp()}.mp3"

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
        """
        Updates the global voice map with new mappings.

        Args:
            new_map (dict): A dictionary of voice mappings to update.
        """
        global VOICE_MAP
        VOICE_MAP.update(new_map)
        if self.debug:
            print(f"[DEBUG] Voice map updated: {VOICE_MAP}", flush=True)
