# filepath: /home/clencyc/Dev/ATDev/ATSms/SmS/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('sendsms/', views.send_sms_view, name='send_sms'),
]