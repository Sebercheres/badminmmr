# clubs/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import Club

class ClubAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            club = Club.objects.get(username=username)
            if club.check_password(password):
                return club
        except Club.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Club.objects.get(pk=user_id)
        except Club.DoesNotExist:
            return None
