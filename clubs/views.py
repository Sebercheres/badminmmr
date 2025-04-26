from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import ClubRegistrationForm
from accounts.models import User
from matches.models import Match

from django.contrib.auth.forms import AuthenticationForm
from django.db import models

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import  Q
from .forms import ClubRegistrationForm

from django.contrib.auth import logout
from django.shortcuts import redirect

import random

@login_required
def kick_user(request, user_id):
    user_to_kick = get_object_or_404(User, id=user_id)
    club = request.user

    # Ensure the logged-in user is a club and the user to kick is in their club
    if club.is_club and user_to_kick.club == club:
        user_to_kick.club = None  # Remove the user from the club
        user_to_kick.save()

    return redirect('club_dashboard')  # Redirect back to Club Dashboard


def register_club(request):
    if request.method == 'POST':
        form = ClubRegistrationForm(request.POST)
        if form.is_valid():
            club = form.save()
            login(request, club, backend='clubs.backends.ClubAuthBackend')  # Log in the club
            return redirect('club_dashboard')  # Redirect to Club Dashboard
    else:
        form = ClubRegistrationForm()
    return render(request, 'clubs/register_club.html', {'form': form})

@login_required
def reset_count(request):
    club = request.user
    online_members = User.objects.filter(club=club, is_online=True)
    for member in online_members:
        member.played_count = 0
        member.save()
    return redirect('club_dashboard')

def club_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            club = authenticate(request, username=username, password=password, backend='clubs.backends.ClubAuthBackend')
            if club is not None and club.is_club:
                login(request, club)
                return redirect('club_dashboard')  # Redirect to Club Dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'clubs/club_login.html', {'form': form})

@login_required
def club_dashboard(request):
    club = request.user
    online_members = User.objects.filter(club=club, is_online=True)  # Fetch online members
    matches = Match.objects.filter(team1__player1__club=club, winner__isnull=True)  # Fetch unscored matches
    # Fetch 5 most recent matches for the club
    match_history = Match.objects.filter(Q(team1__player1__club=club), winner__isnull=False).order_by('-created_at')[:5]

    return render(request, 'clubs/club_dashboard.html', {
        'club': club,
        'online_members': online_members,
        'matches': matches,
        'match_history': match_history,  # Pass match history to the template
    })