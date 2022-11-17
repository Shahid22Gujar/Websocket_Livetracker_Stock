from django.urls import path
from mainapp.views import stockpicker,stocktracker

urlpatterns = [
    path('', stockpicker,name='stockpicker'),
    path('stocktracker/', stocktracker,name='stocktracker'),
]