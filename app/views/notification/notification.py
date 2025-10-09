from app.models import Notification
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta

def notifications():
    