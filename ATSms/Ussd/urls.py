from django.urls import path
from . import views

urlpatterns = [
    path('code/', views.ussd_api, name='ussd_api'),
]