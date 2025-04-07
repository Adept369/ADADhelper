# Royal AI Personal Assistant for ADHD

This project is a scalable, secure backend for a personal assistant tailored for individuals with ADHD. It features WhatsApp integration via Twilio, scheduled affirmations, reflections, and focus time suggestions.

## Project Structure

project-root/ ├── app/ │ ├── init.py │ ├── config.py │ ├── routes.py │ ├── llm.py # (Optional) │ ├── models.py # (Optional) │ └── utils/ │ ├── init.py │ └── helpers.py │ └── static/ │ └── audio/ ├── tests/ │ ├── init.py │ └── test_routes.py ├── celery_app.py ├── tasks.py ├── Dockerfile ├── docker-compose.yml ├── run.py ├── requirements.txt ├── README.md └── Procfile # (Optional)

bash
Copy

## Setup & Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
Set Environment Variables

Create a .env file in the project root and set the following variables:

env
Copy
# OpenAI and ElevenLabs
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_NUMBER=whatsapp:+your_twilio_number
RECIPIENT_PHONE=whatsapp:+recipient_number

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# App Settings
SECRET_KEY=your_secret_key
DATABASE_PATH=custom_archetypes.db
AUDIO_OUTPUT_DIR=app/static/audio
JOURNAL_EXPORT_DIR=exports
UPLOAD_DIR=uploads
Note: Do not commit your .env file to version control. Ensure it's added to your .gitignore.

Install Dependencies

Ensure you have a virtual environment set up (recommended) and run:

bash
Copy
pip install -r requirements.txt
Run the Flask Server

bash
Copy
python run.py
Run Celery Worker and Beat

In separate terminals, execute:

bash
Copy
celery -A celery_app worker --loglevel=info
celery -A celery_app beat --loglevel=info
Docker Deployment (Optional)

To run the app in a containerized environment, build and run the containers with:

bash
Copy
docker-compose up --build
Testing

Run the test suite using either of the following commands:

bash
Copy
pytest
or

bash
Copy
python -m unittest discover -s tests