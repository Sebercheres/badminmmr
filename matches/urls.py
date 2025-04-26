from django.urls import path
from . import views

urlpatterns = [
    path('match/record-result/', views.record_match_result, name='record_match_result'),
    path('club/<int:club_id>/create-random-match/', views.create_random_match, name='create_random_match'),
    path('club/<int:club_id>/matches/', views.club_matches, name='club_matches'),
    path('club/<int:club_id>/matches/<int:match_id>/', views.match_detail, name='match_detail'),
    path('club/<int:club_id>/matches/<int:match_id>/delete/', views.delete_match, name='delete_match'),
    path('club/<int:club_id>/matches/<int:match_id>/edit/', views.edit_match, name='edit_match'),
    path('club/<int:club_id>/matches/create/', views.create_match, name='create_match'),
]
