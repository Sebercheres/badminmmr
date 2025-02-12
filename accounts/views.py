from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import ClubRegistrationForm, UserRegistrationForm, ClubSelectionForm, MatchResultForm
from .models import Club, User, Team, Match
from django.contrib.auth.forms import AuthenticationForm
from django.db import models

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import ClubRegistrationForm, UserRegistrationForm

def register_club(request):
    if request.method == 'POST':
        form = ClubRegistrationForm(request.POST)
        if form.is_valid():
            club = form.save()
            login(request, club, backend='accounts.backends.ClubAuthBackend')  # Log in the club
            return redirect('club_dashboard')  # Redirect to Club Dashboard
    else:
        form = ClubRegistrationForm()
    return render(request, 'accounts/register_club.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='accounts.backends.UserAuthBackend')  # Log in the user
            return redirect('user_dashboard')  # Redirect to User Dashboard
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register_user.html', {'form': form})

@login_required
def user_dashboard(request):
    user = request.user
    club = user.club
    online_users = User.objects.filter(club=club, is_online=True) if club else []

    if request.method == 'POST':
        form = ClubSelectionForm(request.POST)
        if form.is_valid():
            club = form.cleaned_data['club']
            user.club = club
            user.save()
            return redirect('user_dashboard')  # Refresh the page after selecting a club
    else:
        form = ClubSelectionForm()

     # Fetch matches where the user participated and at this club
    user_matches = Match.objects.filter(   
        (models.Q(team1__player1=user) & models.Q(team1__player1__club=club)) |
        (models.Q(team1__player2=user) & models.Q(team1__player2__club=club)) |
        (models.Q(team2__player1=user) & models.Q(team2__player1__club=club)) |
        (models.Q(team2__player2=user) & models.Q(team2__player2__club=club))
    ).order_by('-date_played')  # Order by most recent matches first
    
    return render(request, 'accounts/user_dashboard.html', {
        'club': club,
        'online_users': online_users,
        'form': form,
        'user_matches': user_matches,  # Pass user matches to the template
    })

@login_required
def club_dashboard(request):
    club = request.user
    online_members = User.objects.filter(club=club, is_online=True)  # Fetch online members
    matches = Match.objects.filter(team1__player1__club=club, winner__isnull=True)  # Fetch unscored matches
    match_history = Match.objects.filter(team1__player1__club=club, winner__isnull=False)  # Fetch scored matches

    return render(request, 'accounts/club_dashboard.html', {
        'club': club,
        'online_members': online_members,
        'matches': matches,
        'match_history': match_history,  # Pass match history to the template
    })

# Create Random Match
@login_required
def create_random_match(request):
    club = request.user
    online_users = User.objects.filter(club=club, is_online=True)

    if online_users.count() >= 4:
        # Randomly select 4 unique players
        selected_players = list(online_users.order_by('?')[:4])

        # Get or create Team 1
        team1, created1 = Team.objects.get_or_create(
            player1=selected_players[0],
            player2=selected_players[1],
            defaults={
                'name': f"Team {selected_players[0].username} & {selected_players[1].username}",
            }
        )

        # Get or create Team 2
        team2, created2 = Team.objects.get_or_create(
            player1=selected_players[2],
            player2=selected_players[3],
            defaults={
                'name': f"Team {selected_players[2].username} & {selected_players[3].username}",
            }
        )

        # Create a match
        Match.objects.create(team1=team1, team2=team2)

    return redirect('club_dashboard')  # Redirect back to Club Dashboard

@login_required
def record_match_result(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        team1_score = int(request.POST.get('team1_score'))
        team2_score = int(request.POST.get('team2_score'))

        # Update match scores and determine the winner
        match.team1_score = team1_score
        match.team2_score = team2_score
        match.winner = match.team1 if team1_score > team2_score else match.team2
        match.save()

        # Increment played_count for all players in the match
        players = [match.team1.player1, match.team1.player2, match.team2.player1, match.team2.player2]
        for player in players:
            player.played_count += 1
            player.save()

    return redirect('club_dashboard')  # Redirect back to Club Dashboard

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

def club_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            club = authenticate(request, username=username, password=password, backend='accounts.backends.ClubAuthBackend')
            if club is not None and club.is_club:
                login(request, club)
                return redirect('club_dashboard')  # Redirect to Club Dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/club_login.html', {'form': form})

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