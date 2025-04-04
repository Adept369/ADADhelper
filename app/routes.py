import os
import uuid
from flask import Blueprint, request, Response
from gtts import gTTS
from twilio.rest import Client
from .llm import LLMEngine

main = Blueprint('main', __name__)

@main.route('/webhook', methods=['POST'])
def webhook():
    # Retrieve sender and message from the incoming request
    sender = request.values.get('From')
    incoming_message = request.values.get('Body')
    print(f"Received message from {sender}: {incoming_message}")
    
    # Initialize the LLM engine and generate a response using the incoming message as the prompt
    llm = LLMEngine()
    try:
        generated_response = llm.generate_response(incoming_message)
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        generated_response = "I am sorry, I could not process your request."
    
    text_response = generated_response  # Use the LLM response as our reply
    
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
    
    # Initialize the Twilio client using environment variables
    client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
    twilio_number = os.environ.get("TWILIO_NUMBER")
    
    # Send the text message via the Twilio REST API
    text_message = client.messages.create(
        body=text_response,
        from_=twilio_number,
        to=sender,
        status_callback="https://duck-healthy-easily.ngrok-free.app/status"
    )
    
    # Send the audio message via the Twilio REST API
    media_message = client.messages.create(
        media_url=[media_url],
        from_=twilio_number,
        to=sender,
        status_callback="https://duck-healthy-easily.ngrok-free.app/status"
    )
    
    # Return an empty TwiML response to stop Twilio from sending a default reply
    response_xml = "<?xml version='1.0' encoding='UTF-8'?><Response></Response>"
    return Response(response_xml, mimetype='application/xml')

@main.route('/', methods=['GET'])
def index():
    return "Welcome to the Royal AI Personal Assistant for ADHD", 200

@main.route('/llm', methods=['POST'])
def llm_endpoint():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return Response("No prompt provided", status=400)
    
    llm = LLMEngine()
    try:
        response_text = llm.generate_response(prompt)
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        response_text = "Error processing request."
    
    return Response(response_text, mimetype="text/plain")

@main.route('/status', methods=['POST'])
def status_callback():
    message_sid = request.values.get('MessageSid')
    message_status = request.values.get('MessageStatus')
    error_code = request.values.get('ErrorCode')
    error_message = request.values.get('ErrorMessage')
    
    print(f"Status update for Message SID {message_sid}: {message_status}")
    if error_code or error_message:
        print(f"Error Code: {error_code}, Error Message: {error_message}")
    
    return Response("Status received", status=200)
