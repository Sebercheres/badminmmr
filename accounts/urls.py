from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  # Landing page
    path('login/user/', views.user_login, name='user_login'),  # User login

    path('register/user/', views.register_user, name='register_user'),  # User registration

    path('logout/', views.user_logout, name='user_logout'),  # Logout URL
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('change-club/', views.change_club, name='change_club'),
    path('logout/', views.custom_logout, name='custom_logout'),  # Custom logout URL
    
    # path('match/<int:match_id>/record-result/', views.record_match_result, name='record_match_result'),
    # path('kick-user/<int:user_id>/', views.kick_user, name='kick_user'),  # Kick user URL
    # path('login/club/', views.club_login, name='club_login'),  # Club login
    # path('register/club/', views.register_club, name='register_club'),  # Club registration
    # path('club/dashboard/', views.club_dashboard, name='club_dashboard'),
    # path('club/create-match/', views.create_random_match, name='create_random_match'),
    # path('club/reset_count', views.reset_count, name='reset_count'),
]