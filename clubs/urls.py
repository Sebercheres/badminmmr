from django.urls import path
from . import views

urlpatterns = [
    path('kick-user/<int:user_id>/', views.kick_user, name='kick_user'),  # Kick user URL
    path('login/club/', views.club_login, name='club_login'),  # Club login
    path('register/club/', views.register_club, name='register_club'),  # Club registration
    path('club/dashboard/', views.club_dashboard, name='club_dashboard'),
    path('club/reset_count', views.reset_count, name='reset_count'),
]