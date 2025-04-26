from django.contrib.auth.backends import BaseBackend
from .models import User

# class ClubAuthBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             club = Club.objects.get(username=username)
#             if club.check_password(password):
#                 return club
#         except Club.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             return Club.objects.get(pk=user_id)
#         except Club.DoesNotExist:
#             return None

class UserAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None