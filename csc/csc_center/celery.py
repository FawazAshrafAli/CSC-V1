from celery import Celery
from celery.schedules import crontab
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csc.settings')

# Define Celery app
app = Celery('csc')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Configuration
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

# Define the periodic task schedule
# app.conf.beat_schedule = {
#     'check-csc-center-every-day': {
#         'task': 'csc_center.tasks.check_validity',
#         'schedule': crontab(hour=17, minute=30),  # Runs every day at 17:05 (5:05 PM)
#     },
# }

app.conf.beat_schedule = {
    'check-csc-center-every-minute': {
        'task': 'csc_center.tasks.check_validity',
        'schedule': crontab(minute='*'),  # Runs every minute
    },
}
