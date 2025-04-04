import os
from celery import Celery
from celery.schedules import crontab

celery = Celery('tasks', broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'))

celery.conf.update(
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    beat_schedule={
        'send-morning-affirmation-everyday': {
            'task': 'tasks.send_morning_affirmation',
            'schedule': crontab(hour=7, minute=0),  # 7:00 AM every day
            'args': (os.environ.get("RECIPIENT_PHONE"),)
        },
        'send-evening-reflection-everyday': {
            'task': 'tasks.send_evening_reflection',
            'schedule': crontab(hour=21, minute=0),  # 9:00 PM every day
            'args': (os.environ.get("RECIPIENT_PHONE"),)
        },
        'send-focus-time-suggestion-every-hour': {
            'task': 'tasks.send_focus_time_suggestion',
            'schedule': crontab(minute=0, hour='10-16'),  # every hour from 10 AM to 4 PM
            'args': (os.environ.get("RECIPIENT_PHONE"),)
        },
    }
)
