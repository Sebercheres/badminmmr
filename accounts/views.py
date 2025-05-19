from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ClubSelectionForm
from .models import User
from matches.models import Match

from django.contrib.auth.forms import AuthenticationForm
from django.db import models

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import  Q

from django.contrib.auth import logout
from django.shortcuts import redirect

import random

def custom_logout(request):
    user_logout(request)
    return redirect('landing_page')  # Redirect to the landing page after logout

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            
            user = form.save()
            return redirect('landing_page')  # Redirect to User Dashboard
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register_user.html', {'form': form})

@login_required
def user_dashboard(request):
    user = request.user
    club = user.club
    online_users = User.objects.filter(club=club, is_online=True) if club else []

    # Fetch matches where the user participated and are associated with the current club
    user_matches = Match.objects.filter(
        (models.Q(team1__player1=user, team1__player2__club=club) |
         models.Q(team1__player2=user, team1__player1__club=club) |
         models.Q(team2__player1=user, team2__player2__club=club) |
         models.Q(team2__player2=user, team2__player1__club=club))
    ).order_by('-created_at')  # Order by most recent matches first

    # Club selection form
    if request.method == 'POST':
        form = ClubSelectionForm(request.POST)
        if form.is_valid():
            club = form.cleaned_data['club']
            user.club = club
            user.played_count = 0  # Reset played_count when changing clubs
            user.save()
            return redirect('user_dashboard')  # Refresh the page after selecting a club
    else:
        form = ClubSelectionForm()

    return render(request, 'accounts/user_dashboard.html', {
        'club': club,
        'online_users': online_users,
        'user_matches': user_matches,
        'form': form,
    })

def landing_page(request):
    return render(request, 'accounts/landing_page.html')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password, backend='accounts.backends.UserAuthBackend')
            if user is not None and user.is_user:
                user.is_online = True  # Set user online
                user.save()
                login(request, user)
                return redirect('user_dashboard')  # Redirect to User Dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/user_login.html', {'form': form})


@login_required
def user_logout(request):
    user = request.user
    user.is_online = False  # Set user offline
    user.save()
    logout(request)  # Log out the user
    return redirect('landing_page')  # Redirect to Club login page

@login_required
def change_club(request):
    user = request.user
    user.club = None
    user.save()
    return redirect('user_dashboard')
