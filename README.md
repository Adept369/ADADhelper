# Royal AI Personal Assistant for ADHD

This project is a scalable, secure backend for a personal assistant tailored for individuals with ADHD, featuring WhatsApp integration via Twilio, scheduled affirmations, reflections, and focus time suggestions.

## Project Structure

project-root/ ├── app/ │ ├── init.py │ ├── config.py │ ├── routes.py │ ├── llm.py (Optional) │ ├── models.py (Optional) │ └── utils/ │ ├── init.py │ └── helpers.py │ └── static/ │ └── audio/ ├── tests/ │ ├── init.py │ └── test_routes.py ├── celery_app.py ├── tasks.py ├── Dockerfile ├── docker-compose.yml ├── run.py ├── requirements.txt ├── README.md └── Procfile (Optional)


## Setup & Installation

1. **Clone the Repository**

2. **Set Environment Variables**

   Ensure you have the following set:
   - `SECRET_KEY`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_NUMBER` (WhatsApp-enabled sender number)
   - `RECIPIENT_PHONE` (WhatsApp recipient number)
   - `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` (if not using defaults)

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
4. Run the Flask Server

  ```bash
   python run.py
5. Run Celery Worker and Beat

    In separate terminals, run:

    celery -A celery_app worker --loglevel=info
    celery -A celery_app beat --loglevel=info
    Docker (Optional)

6. To run in a containerized environment:


    docker-compose up --build