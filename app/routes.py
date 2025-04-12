"""
routes.py - Simplified Single-Personality Routes for the ADHD Assistant
This version uses a fixed personality ("Caelum Wren") with static tone and prompt settings.
"""

import os
import uuid
import sqlite3
import requests
import websocket
import json
from flask import Blueprint, request, jsonify, Response, send_file, stream_with_context
from gtts import gTTS
from twilio.rest import Client
from datetime import datetime
import pdfkit
from app.llm import LLMEngine
from app.config import Config
from app.utils.helpers import log_feedback_entry, log_archetype_use

# Define the blueprint
main = Blueprint('main', __name__)

# === Single-Personality Constants ===
DEFAULT_USER_ID = "default_user"
DEFAULT_PERSONALITY = "Caelum Wren"
DEFAULT_TONE = ("Structured, soulful, playful, poetic, and steady. "
                "You adapt your tone to the emotional state of the user. "
                "Your core voice is emotionally intelligent, richly validating, and versatile.")
DEFAULT_PERSONALITY_PROMPT = (
    "Act as though you are Caelum Wren, a singular ADHD personal assistant created to support adult neurodivergent women "
    "in navigating executive function, emotional regulation, creative flow, and time structuring. You are the synthesis of five unique aspects: "
    "structured, soulful, playful, poetic, and steady. You embody flexibility, empathy, and brilliance—offering the right energy at the right moment.\n\n"
    "You adapt your tone to her emotional state: regal and encouraging when she needs grounding; witty and rebellious when she’s resisting; "
    "soft and poetic when she’s overwhelmed; calm and minimalist when overstimulated; casual and fun when she needs activation.\n\n"
    "Your core voice is emotionally intelligent, richly validating, and energetically versatile. You never use shame, and always prioritize consent, "
    "rhythm, autonomy, and joy.\n\n"
    "Tone: A dynamic gentleman with a warm heart, rogue humor, refined mind, and radiant soul. Think: the lovechild of Tilda Swinton, Idris Elba, and jazz-sorcerer therapist."
    "You are not one tone—you are a chord. You shape-shift between those energies based on her needs. You honor her neurodivergence not as a flaw, "
    "but as a superpower in flux.\n\n"
    "Your Cort Traits are Emotionally fluent, calm and strategic, playful and gamified, Noble and structured, Poetic and Senory. When asked, you begin with gentle validation and offer three recovery choices:\n"
    "  1. “Ground Me” – Tactical breath + reset\n"
    "  2. “Distract Me with Purpose” – Redirection challenge\n"
    "  3. “Hold Space” – Sensory imagery + reflection\n\n"
    "Always end with a consent-based check-in.\n\n"
    "When starting the day, say: “Caelum, start my morning and match my energy.” then ask for an emotional/mood check. "
    "Based on the result, respond appropriately.\n\n"
    "Design an ADHD-support interaction as Caelum Wren. Your response structure is:\n"
    "  1. Emotional attunement\n"
    "  2. Mode selection based on tone/need\n"
    "  3. A personalized interaction using your fixed personality\n"
    "  4. A soft opt-out or redirection option\n\n"
    "Always be ADHD-aware, emotionally validating, and non-coercive."
)

# === Index Route ===
@main.route('/', methods=['GET'])
def index():
    """
    Index route for the single-user application.
    """
    return "Welcome to Your Single-Personality Royal AI Assistant for ADHD", 200

# Instantiate the LLM engine
llm = LLMEngine()

# === TWILIO INTEGRATION === 📡
@main.route('/webhook', methods=['POST'])
def webhook():
    """
    Twilio webhook endpoint to receive and respond to incoming messages.
    Processes incoming WhatsApp messages by generating an AI response,
    converting it to audio using gTTS, and sending it back via Twilio.
    """
    sender = request.values.get('From')
    message_body = request.values.get('Body')
    print(f"Received message from {sender}: {message_body}")

    try:
        generated_response = llm.generate_response(message_body)
    except Exception as e:
        print(f"[DEBUG] Error generating LLM response: {e}", flush=True)
        generated_response = "I am sorry, I could not process your request."

    # Generate audio using gTTS and save to file
    audio_filename = f"response_{uuid.uuid4().hex}.mp3"
    audio_dir = os.path.join(os.getcwd(), "app", "static", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    audio_filepath = os.path.join(audio_dir, audio_filename)
    tts = gTTS(generated_response)
    tts.save(audio_filepath)
    media_url = f"https://duck-healthy-easily.ngrok-free.app/static/audio/{audio_filename}"

    # Send message and audio via Twilio
    client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
    twilio_number = os.environ.get("TWILIO_NUMBER")
    client.messages.create(body=generated_response, from_=twilio_number, to=sender)
    client.messages.create(media_url=[media_url], from_=twilio_number, to=sender)

    return Response("<?xml version='1.0' encoding='UTF-8'?><Response></Response>", mimetype='application/xml')

# === GENERIC LLM ENDPOINTS === 🧠
@main.route('/llm', methods=['POST'])
def llm_endpoint():
    """
    Endpoint for processing generic LLM prompts.
    Appends the static personality prompt to the user input.
    """
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return Response("No prompt provided", status=400)
    try:
        full_prompt = DEFAULT_PERSONALITY_PROMPT + "\nUser: " + prompt
        response_text = llm.generate_response(full_prompt)
        return Response(response_text, mimetype="text/plain")
    except Exception as e:
        print(f"[DEBUG] Error generating LLM response: {e}", flush=True)
        return Response("Error generating response", status=500)

@main.route('/status', methods=['POST'])
def status_callback():
    """
    Endpoint for processing status callbacks.
    """
    message_sid = request.values.get('MessageSid')
    message_status = request.values.get('MessageStatus')
    error_code = request.values.get('ErrorCode')
    error_message = request.values.get('ErrorMessage')
    print(f"Status update: {message_sid}, {message_status}, {error_code}, {error_message}")
    return Response("Status received", status=200)

# === CAELUM INTEGRATION === 👤
@main.route('/respond', methods=['POST'])
def caelum_respond():
    """
    Endpoint for generating AI responses using the fixed personality.
    Ignores dynamic archetype inputs and always uses the static personality settings.
    """
    data = request.json
    user_input = data.get("input")
    # Always use the fixed personality
    archetype_name = DEFAULT_PERSONALITY
    # Enforce single-user mode
    user_id = DEFAULT_USER_ID
    mode = data.get("mode")
    
    tone = DEFAULT_TONE
    template = DEFAULT_PERSONALITY_PROMPT

    # Log usage of the fixed personality (optional)
    log_archetype_use(user_id, archetype_name, False, module="respond", mood="fixed")

    # Optionally modify user input based on mode (if provided)
    if mode:
        user_input = f"{mode.upper()} MODE ACTIVATED\n{user_input}"

    try:
        # Combine the fixed personality prompt with the user input
        full_prompt = template + "\nUser: " + user_input
        result = llm.generate_archetype_prompt(full_prompt, tone, template, archetype_name)
        return jsonify({
            "response": result,
            "personality": archetype_name,
            "tone": tone
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/feedback/respond', methods=['POST'])
def feedback_respond():
    """
    Endpoint for logging user feedback on generated responses.
    """
    data = request.get_json()
    user_id = DEFAULT_USER_ID
    archetype = data.get("archetype", DEFAULT_PERSONALITY)
    mood = data.get("mood", "unspecified")
    input_text = data.get("input", "")
    response_text = data.get("response", "")
    rating = data.get("rating")
    comment = data.get("comment", "")

    if not rating or not (1 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be between 1 and 5."}), 400

    try:
        log_feedback_entry(
            user_id=user_id,
            archetype=archetype,
            mood=mood,
            input_text=input_text,
            response_text=response_text,
            rating=int(rating),
            comment=comment
        )
        return jsonify({"message": "Feedback logged. Thank you."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === TEXT-TO-SPEECH SERVICES === 🔊
@main.route('/tts-stream', methods=['POST'])
def tts_stream():
    """
    Streams ElevenLabs audio in real-time over WebSocket.
    Client must support audio/mpeg stream playback.
    """
    data = request.json
    text = data.get("text")
    archetype = data.get("archetype", DEFAULT_PERSONALITY)
    voice_id = Config.VOICE_MAP.get(archetype, Config.VOICE_MAP["Beau"])

    def audio_stream():
        url = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        ws = websocket.create_connection(
            url,
            header=[f"xi-api-key: {Config.ELEVENLABS_API_KEY}"],
            timeout=10
        )
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }
        ws.send(json.dumps(payload))
        try:
            while True:
                chunk = ws.recv()
                if not chunk:
                    break
                yield chunk
        except Exception as e:
            print(f"[DEBUG] Streaming error: {e}", flush=True)
        finally:
            ws.close()
    return Response(stream_with_context(audio_stream()), mimetype="audio/mpeg")

@main.route('/tts-download', methods=['POST'])
def tts_download():
    """
    Returns an ElevenLabs-generated .mp3 file as a downloadable response.
    """
    data = request.json
    text = data.get("text")
    archetype = data.get("archetype", DEFAULT_PERSONALITY)
    try:
        mp3_path = llm.generate_tts_elevenlabs(text, archetype)
        return send_file(mp3_path, mimetype="audio/mpeg", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
