import os

from celery import Celery
from kombu import Queue, Exchange

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('server')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


BASE_DB_WORKER_QUEUE_ROUTE = {'queue': 'car_db_worker', 'routing_key': 'car_db_worker'}
BASE_TASK_MANAGER_ROUTE = {'queue': 'manager_task', 'routing_key': 'manager_task'}
BASE_PAGE_CRAWLER_ROUTE = {'queue': 'car_page_scraper', 'routing_key': 'car_page_scraper'}
SPREADSHEETS_WORKER_ROUTE = {'queue': 'spreadsheets_worker', 'routing_key': 'spreadsheets_worker'}


app.conf.task_routes = {

    'autoria.tasks.car_page_scraper': BASE_PAGE_CRAWLER_ROUTE,

    'autoria.tasks.car_db_worker': BASE_DB_WORKER_QUEUE_ROUTE,

    'autoria.tasks.manager_task': BASE_TASK_MANAGER_ROUTE,

    'autoria.tasks.spreadsheets_worker': SPREADSHEETS_WORKER_ROUTE,

}
