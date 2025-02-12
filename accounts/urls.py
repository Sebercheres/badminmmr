from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  # Landing page
    path('login/user/', views.user_login, name='user_login'),  # User login
    path('login/club/', views.club_login, name='club_login'),  # Club login
    path('register/user/', views.register_user, name='register_user'),  # User registration
    path('register/club/', views.register_club, name='register_club'),  # Club registration
    path('logout/', views.user_logout, name='user_logout'),  # Logout URL
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('club/dashboard/', views.club_dashboard, name='club_dashboard'),
    path('club/create-match/', views.create_random_match, name='create_random_match'),
    path('match/<int:match_id>/record-result/', views.record_match_result, name='record_match_result'),
    path('change-club/', views.change_club, name='change_club'),
]