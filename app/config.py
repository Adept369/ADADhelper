import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = False
    TESTING = False

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

    DATABASE_PATH = os.getenv("DATABASE_PATH", "custom_archetypes.db")
    AUDIO_OUTPUT_DIR = os.getenv("AUDIO_OUTPUT_DIR", "app/static/audio")
    JOURNAL_EXPORT_DIR = os.getenv("JOURNAL_EXPORT_DIR", "exports")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

    VOICE_MAP = {
        "Beau": "21m00Tcm4TlvDq8ikWAM",
        "Fox": "TxGEqnHWrfWFTfGW9XjX",
        "Jasper": "AZnzlk1XvdvUeBnXmlld",
        "Orion": "EXAVITQu4vr4xnSDxMaL",
        "Theo": "MF3mGyEYCl7XYWbV9V6O"
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
