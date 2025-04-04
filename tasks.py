import os
import uuid
from celery_app import celery
from twilio.rest import Client
from gtts import gTTS
import os

# Twilio credentials from environment variables
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_NUMBER")  # WhatsApp-enabled sender number

client = Client(account_sid, auth_token)

@celery.task
def send_morning_affirmation(recipient):
    if not recipient:
        recipient = "whatsapp:+14058333638"  # Default value for testing
    affirmation = "Good morning! You are capable, resilient, and ready to seize the day!"
    media_url = generate_audio_message(affirmation)
    message = client.messages.create(
        body=affirmation,
        media_url=[media_url],
        from_=twilio_number,
        to=recipient,
        statusCallback="https://duck-healthy-easily.ngrok-free.app//status"
    )
    return message.sid


def generate_audio_message(text_response):
    # Generate a unique filename for the audio file
    audio_filename = f"response_{uuid.uuid4().hex}.mp3"
    audio_dir = os.path.join(os.getcwd(), "app", "static", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    audio_filepath = os.path.join(audio_dir, audio_filename)
    
    # Generate the audio file using gTTS
    tts = gTTS(text_response)
    tts.save(audio_filepath)
    
    # Construct the media URL using your static domain
    media_url = f"https://duck-healthy-easily.ngrok-free.app/static/audio/{audio_filename}"
    return media_url


@celery.task
def send_morning_affirmation(recipient):
    affirmation = "Good morning! You are capable, resilient, and ready to seize the day!"
    media_url = generate_audio_message(affirmation)
    message = client.messages.create(
        body=affirmation,
        media_url=[media_url],
        from_=twilio_number,
        to=recipient
    )
    return message.sid

@celery.task
def send_evening_reflection(recipient):
    reflection = "Good evening. Take a moment to reflect on your day, celebrate your victories, and learn from your challenges."
    media_url = generate_audio_message(reflection)
    message = client.messages.create(
        body=reflection,
        media_url=[media_url],
        from_=twilio_number,
        
        to=recipient
    )
    return message.sid

@celery.task
def send_focus_time_suggestion(recipient):
    suggestion = (
        "This is your moment for focused self-improvement. "
        "Consider spending 15 minutes in quiet reflection, reading an inspiring article, or planning your next step towards a better tomorrow."
    )
    media_url = generate_audio_message(suggestion)
    message = client.messages.create(
        body=suggestion,
        media_url=[media_url],
        from_=twilio_number,
        to=recipient
    )
    return message.sid
