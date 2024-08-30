import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_itu_change.settings')

app = Celery('django_itu_change')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

