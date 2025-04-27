from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models

from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth import logout
from django.shortcuts import redirect

from .forms import TeamCreationForm

from .models import Team, TeamDetail
from accounts.models import User
from clubs.models import Club

@login_required
def create_team(request):
    if request.method == "POST":
        form = TeamCreationForm(request.POST)
        
        if form.is_valid():
            team = form.save(commit=False)
            team.club = request.user
            team.save()
            messages.success(request, "Team created successfully!")
            return redirect("team_detail", team_id=team.id)
    else:
        form = TeamCreationForm()
    
    players = User.objects.filter(club=request.user, is_active=True)
    return render(request, "teams/create_team.html", {"form": form, "players": players})

@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    team_details = TeamDetail.objects.filter(team=team)
    return render(request, "teams/team_detail.html", {"team": team, "team_details": team_details, "club_id": team.club.id})

@login_required
def edit_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == "POST":
        form = TeamCreationForm(request.POST, instance=team)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Team updated successfully!")
            return redirect("team_detail", team_id=team.id)
    else:
        form = TeamCreationForm(instance=team)
    return render(request, "teams/edit_team.html", {"form": form, "team": team})

@login_required
def club_teams(request, club_id):
    club  = get_object_or_404(Club, id=club_id)
    teams = Team.objects.filter(club=request.user)
    
    return render(request, "teams/club_teams.html", {"teams": teams, "club": club})

@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == "POST":
        team.delete()
        messages.success(request, "Team deleted successfully!")
        return redirect("club_teams", club_id=team.club.id)
    
    return render(request, "teams/delete_team.html", {"team": team})