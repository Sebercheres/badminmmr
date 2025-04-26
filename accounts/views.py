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

# @login_required
# def club_dashboard(request):
#     club = request.user
#     online_members = User.objects.filter(club=club, is_online=True)  # Fetch online members
#     matches = Match.objects.filter(team1__player1__club=club, winner__isnull=True)  # Fetch unscored matches
#     match_history = Match.objects.filter(team1__player1__club=club, winner__isnull=False)  # Fetch scored matches

#     return render(request, 'accounts/club_dashboard.html', {
#         'club': club,
#         'online_members': online_members,
#         'matches': matches,
#         'match_history': match_history,  # Pass match history to the template
#     })

# @login_required
# def reset_count(request):
#     club = request.user
#     online_members = User.objects.filter(club=club, is_online=True)
#     for member in online_members:
#         member.played_count = 0
#         member.save()
#     return redirect('club_dashboard')

# @login_required
# def kick_user(request, user_id):
#     user_to_kick = get_object_or_404(User, id=user_id)
#     club = request.user

#     # Ensure the logged-in user is a club and the user to kick is in their club
#     if club.is_club and user_to_kick.club == club:
#         user_to_kick.club = None  # Remove the user from the club
#         user_to_kick.save()

#     return redirect('club_dashboard')  # Redirect back to Club Dashboard


# def register_club(request):
#     if request.method == 'POST':
#         form = ClubRegistrationForm(request.POST)
#         if form.is_valid():
#             club = form.save()
#             login(request, club, backend='accounts.backends.ClubAuthBackend')  # Log in the club
#             return redirect('club_dashboard')  # Redirect to Club Dashboard
#     else:
#         form = ClubRegistrationForm()
#     return render(request, 'accounts/register_club.html', {'form': form})

# def club_login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             club = authenticate(request, username=username, password=password, backend='accounts.backends.ClubAuthBackend')
#             if club is not None and club.is_club:
#                 login(request, club)
#                 return redirect('club_dashboard')  # Redirect to Club Dashboard
#     else:
#         form = AuthenticationForm()
#     return render(request, 'accounts/club_login.html', {'form': form})

# matches

# @login_required
# def record_match_result(request, match_id):
#     match = get_object_or_404(Match, id=match_id)
#     if request.method == 'POST':
#         team1_score = int(request.POST.get('team1_score'))
#         team2_score = int(request.POST.get('team2_score'))

#         # Update match scores and determine the winner
#         match.team1_score = team1_score
#         match.team2_score = team2_score
#         match.winner = match.team1 if team1_score > team2_score else match.team2
#         match.save()

#         # Update MMR for players in the winning team (+25)
#         for player in [match.winner.player1, match.winner.player2]:
#             player.mmr += 25
#             player.played_count += 1  # Increment played count  
#             player.save()

#         # Update MMR for players in the losing team (-25)
#         losing_team = match.team2 if match.winner == match.team1 else match.team1
#         for player in [losing_team.player1, losing_team.player2]:
#             player.played_count += 1  # Increment played count
#             player.mmr = max(player.mmr - 25, 0)  # Ensure MMR doesn't go below 0
#             player.save()

#     return redirect('club_dashboard')  # Redirect back to Club Dashboard

# @login_required
# def create_random_match(request):
#     club = request.user

#     try:
#         # Get all ongoing matches in this club
#         ongoing_matches = Match.objects.filter(
#             Q(team1__player1__club=club) | 
#             Q(team1__player2__club=club) |
#             Q(team2__player1__club=club) |
#             Q(team2__player2__club=club),
#             winner__isnull=True
#         )

#         busy_players = set()
#         for match in ongoing_matches:
#             busy_players.update([
#                 match.team1.player1_id,
#                 match.team1.player2_id,
#                 match.team2.player1_id,
#                 match.team2.player2_id
#             ])

#         available_players = User.objects.filter(
#             club=club,
#             is_online=True
#         ).exclude(
#             id__in=busy_players
#         ).order_by('played_count')  # Order by played_count directly

#         if available_players.count() < 4:
#             messages.warning(request, "Not enough available players (need at least 4).")
#             return redirect('club_dashboard')

#         # Convert to list for easier manipulation
#         players_ordered = list(available_players)
        
#         match_created = False
#         max_attempts = 10  # Prevent infinite loops
#         attempt = 0
        
#         while not match_created and attempt < max_attempts:
#             attempt += 1
            
#             # Shuffle players while maintaining the played_count order
#             # We'll group players with similar played_counts and shuffle within groups
#             groups = {}
#             for player in players_ordered:
#                 if player.played_count not in groups:
#                     groups[player.played_count] = []
#                 groups[player.played_count].append(player)
            
#             # Rebuild the list with shuffled groups
#             shuffled_players = []
#             for count in sorted(groups.keys()):
#                 random.shuffle(groups[count])
#                 shuffled_players.extend(groups[count])
            
#             # Try to find a group where the first 4 players have similar play counts
#             for i in range(len(shuffled_players) - 3):
#                 candidate_group = shuffled_players[i:i+4]
#                 max_diff = max(p.played_count for p in candidate_group) - min(p.played_count for p in candidate_group)
                
#                 # Allow some flexibility in play count difference
#                 if max_diff <= 2:
#                     # Try all possible team combinations
#                     team_pairings = [
#                         ((candidate_group[0], candidate_group[1]), (candidate_group[2], candidate_group[3])),
#                         ((candidate_group[0], candidate_group[2]), (candidate_group[1], candidate_group[3])),
#                         ((candidate_group[0], candidate_group[3]), (candidate_group[1], candidate_group[2])),
#                     ]
#                     random.shuffle(team_pairings)
                    
#                     for team1_players, team2_players in team_pairings:
#                         team1, _ = Team.objects.get_or_create(
#                             player1=team1_players[0],
#                             player2=team1_players[1],
#                             defaults={'name': f"Team {team1_players[0].username} & {team1_players[1].username}"}
#                         )
#                         team2, _ = Team.objects.get_or_create(
#                             player1=team2_players[0],
#                             player2=team2_players[1],
#                             defaults={'name': f"Team {team2_players[0].username} & {team2_players[1].username}"}
#                         )

#                         # Avoid repeating match combos
#                         if not Match.objects.filter(
#                             Q(team1=team1, team2=team2) | Q(team1=team2, team2=team1)
#                         ).exists():
#                             Match.objects.create(team1=team1, team2=team2)
#                             messages.success(request, "New match created successfully!")
#                             match_created = True
#                             break
                    
#                     if match_created:
#                         break
            
#             if not match_created:
#                 # If we couldn't find a perfect group, try with the 4 least played players
#                 candidate_group = players_ordered[:4]
                
#                 team_pairings = [
#                     ((candidate_group[0], candidate_group[1]), (candidate_group[2], candidate_group[3])),
#                     ((candidate_group[0], candidate_group[2]), (candidate_group[1], candidate_group[3])),
#                     ((candidate_group[0], candidate_group[3]), (candidate_group[1], candidate_group[2])),
#                 ]
#                 random.shuffle(team_pairings)
                
#                 for team1_players, team2_players in team_pairings:
#                     team1, _ = Team.objects.get_or_create(
#                         player1=team1_players[0],
#                         player2=team1_players[1],
#                         defaults={'name': f"Team {team1_players[0].username} & {team1_players[1].username}"}
#                     )
#                     team2, _ = Team.objects.get_or_create(
#                         player1=team2_players[0],
#                         player2=team2_players[1],
#                         defaults={'name': f"Team {team2_players[0].username} & {team2_players[1].username}"}
#                     )

#                     if not Match.objects.filter(
#                         Q(team1=team1, team2=team2) | Q(team1=team2, team2=team1)
#                     ).exists():
#                         Match.objects.create(team1=team1, team2=team2)
#                         messages.success(request, "New match created successfully!")
#                         match_created = True
#                         break

#         if not match_created:
#             messages.warning(request, "No valid new match combination could be formed.")

#     except Exception as e:
#         messages.error(request, f"Error creating match: {str(e)}")

#     return redirect('club_dashboard')