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
from markdown import markdown
import pdfkit
from app.llm import LLMEngine
from app.config import Config
from app.utils.helpers import (
    get_recent_mood_summary,
    map_mood_to_archetype,
    log_archetype_use,
    get_prompt_scaffold,
    log_feedback_entry
)

# Define the blueprint
main = Blueprint('main', __name__)

# Constant for single-user mode (all requests use this user_id)
DEFAULT_USER_ID = "default_user"

# === Index Route ===
@main.route('/', methods=['GET'])
def index():
    """
    Index route for the single-user application.
    """
    return "Welcome Lighting Dove to Your Majesty's Royal AI Personal Assistant for ADHD", 200

# Instantiate the LLM engine
llm = LLMEngine()

# === TWILIO INTEGRATION === 📡
@main.route('/webhook', methods=['POST'])
def webhook():
    """
    Twilio webhook endpoint to receive and respond to incoming messages.
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
    """
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return Response("No prompt provided", status=400)
    try:
        response_text = llm.generate_response(prompt)
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
    Endpoint for generating AI responses with archetype-based tone adaptation.
    In single-user mode, the user_id is always set to DEFAULT_USER_ID.
    """
    data = request.json
    user_input = data.get("input")
    archetype_name = data.get("custom_archetype")
    # Enforce single-user mode
    user_id = DEFAULT_USER_ID
    mode = data.get("mode")

    tone = None
    template = None

    # Determine tone and archetype based on recent mood if no archetype is provided
    if not archetype_name:
        recent_moods = get_recent_mood_summary(user_id, top_n=1)
        mood_based = map_mood_to_archetype(recent_moods[0]) if recent_moods else {
            "archetype": "Beau",
            "tone": "Warm, structured"
        }
        archetype_name = mood_based["archetype"]
        tone = mood_based["tone"]
    else:
        recent_moods = []

    # Fetch prompt template from the database using the configured database path
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT tone, template FROM archetypes WHERE name = ?", (archetype_name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        tone = tone or row[0]
        template = row[1]
    else:
        tone = tone or "Warm, structured"
        template = "[Beau Mode]\nGently respond."

    mood_used = recent_moods[0] if recent_moods else "unspecified"
    is_custom = archetype_name not in ["Beau", "Fox", "Jasper", "Theo", "Orion"]
    log_archetype_use(user_id, archetype_name, is_custom, module="respond", mood=mood_used)

    # Prepend a preset prompt scaffold if a mode is specified
    if mode:
        scaffold = get_prompt_scaffold(mode)
        if scaffold:
            user_input = f"{scaffold}\n{user_input}"

    try:
        result = llm.generate_archetype_prompt(user_input, tone, template, archetype_name)
        return jsonify({
            "response": result,
            "archetype_used": archetype_name,
            "tone": tone,
            "mood_used": mood_used,
            "mode": mode
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/feedback/respond', methods=['POST'])
def feedback_respond():
    """
    Endpoint for logging user feedback on generated responses.
    """
    data = request.get_json()
    # Enforce single-user mode
    user_id = DEFAULT_USER_ID
    archetype = data.get("archetype", "Beau")
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
    archetype = data.get("archetype", "Beau")
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
    archetype = data.get("archetype", "Beau")
    try:
        mp3_path = llm.generate_tts_elevenlabs(text, archetype)
        return send_file(mp3_path, mimetype="audio/mpeg", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
