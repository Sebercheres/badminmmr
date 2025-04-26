from django.urls import path
from . import views

urlpatterns = [
    path("teams/create/", views.create_team, name="create_team"),  # Create team URL
    path("teams/<int:team_id>/", views.team_detail, name="team_detail"),  # Team detail URL
    path("teams/<int:club_id>", views.club_teams, name="club_teams"),  # List all teams URL
    path("teams/<int:team_id>/edit/", views.edit_team, name="edit_team"),  # Edit team URL
    path("teams/<int:team_id>/delete/", views.delete_team, name="delete_team"),  # Delete team URL
]
