from __future__ import absolute_import,unicode_literals
import os
from celery import Celery
from django.conf import settings
# from celery.schedules import crontabs
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockproject.settings')

app=Celery('stockproject')
app.conf.enable_utc=False
app.conf.update(timezoe='Asia/Kolkata')
app.config_from_object(settings,namespace='CELERY')
app.conf.beat_schedule ={
    'every-10-seconds':{
        'task':'mainapp.tasks.update_stock', #appname.tasks.nameoftask
        'schedule':10,
        'args':(['RELIANCE.NS','BAJAJFINSV.NS'],)
    },
}

#to get updated task from celery
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')