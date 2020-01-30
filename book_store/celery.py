import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_store.settings')

app = Celery('book_store')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
response = app.control.enable_events(reply=True)
print(response)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))