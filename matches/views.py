from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from accounts.models import User
from clubs.models import Club
from .models import Match
from teams.models import TeamDetail
from teams.models import Team
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import  Q
from django.db import transaction

from django.contrib.auth import logout
from django.shortcuts import redirect

import random
import math
from .forms import MatchResultForm, MatchCreationForm



@login_required
def record_match_result(request):
    if request.method == 'POST':
        form = MatchCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                match = form.save(commit=True)  # Save the match, which now includes scores
                
                # Create TeamDetail instances for winner and loser
                if match.winner and match.loser:
                    # Calculate average ratings for both teams
                    avg_rating_winner = match.winner.get_average_mmr()
                    avg_rating_loser = match.loser.get_average_mmr()
                    
                    winner_score = match.team1_score if match.winner == match.team1 else match.team2_score
                    loser_score = match.team2_score if match.winner == match.team1 else match.team1_score
                    
                    match_played_count_winner_player1 = match.winner.player1.matched_played_count
                    winner_player1_mmr_change= math.ceil(calculate_player_mmr_change(match.winner.player1.mmr, winner_score, loser_score, 1, avg_rating_loser, match_played_count_winner_player1))
                    
                    match_played_count_winner_player2 = match.winner.player2.matched_played_count
                    winner_player2_mmr_change = math.ceil(calculate_player_mmr_change(match.winner.player2.mmr, winner_score, loser_score, 1, avg_rating_loser, match_played_count_winner_player2))
                    
                    match_played_count_loser_player1 = match.loser.player1.matched_played_count
                    loser_player1_mmr_change = math.ceil(calculate_player_mmr_change(match.loser.player1.mmr, loser_score, winner_score, 0, avg_rating_winner, match_played_count_loser_player1))
                    
                    match_played_count_loser_player2 = match.loser.player2.matched_played_count
                    loser_player2_mmr_change = math.ceil(calculate_player_mmr_change(match.loser.player2.mmr, loser_score, winner_score, 0, avg_rating_winner, match_played_count_loser_player2))
                    
                    

                    # Create TeamDetail instances
                    TeamDetail.objects.create(
                        team=match.winner,
                        match=match,
                        player1_mmr_change=winner_player1_mmr_change,
                        player2_mmr_change=winner_player2_mmr_change
                    )
                    TeamDetail.objects.create(
                        team=match.loser,
                        match=match,
                        player1_mmr_change=loser_player1_mmr_change,
                        player2_mmr_change=loser_player2_mmr_change
                    )
                    
                
                messages.success(request, "Match created successfully.")
                return redirect('club_dashboard')
    else:
        form = MatchCreationForm()

    return redirect('club_dashboard')  # Redirect back to Club Dashboard

@login_required
def create_random_match(request, club_id):
    club = request.user
    try:
        ongoing_matches = get_ongoing_matches(club)
        busy_players = get_busy_players(ongoing_matches)

        available_players = get_available_players(club, busy_players)
        if available_players.count() < 4:
            messages.warning(request, "Not enough available players (need at least 4).")
            return redirect('club_dashboard')

        players_ordered = list(available_players)
        match_created = attempt_to_create_match(request, club, players_ordered)  # Pass request here

        if not match_created:
            messages.warning(request, "No valid new match combination could be formed.")

    except Exception as e:
        messages.error(request, f"Error creating match: {str(e)}")

    return redirect('club_dashboard')


def get_ongoing_matches(club):
    return Match.objects.filter(
        Q(team1__player1__club=club) | 
        Q(team1__player2__club=club) |
        Q(team2__player1__club=club) |
        Q(team2__player2__club=club),
        winner__isnull=True
    )


def get_busy_players(ongoing_matches):
    busy_players = set()
    for match in ongoing_matches:
        busy_players.update([
            match.team1.player1_id,
            match.team1.player2_id,
            match.team2.player1_id,
            match.team2.player2_id
        ])
    return busy_players


def get_available_players(club, busy_players):
    return User.objects.filter(
        club=club,
        is_online=True
    ).exclude(
        id__in=busy_players
    ).order_by('played_count')


def attempt_to_create_match(request, club, players_ordered):  # Accept request here
    max_attempts = 10
    for attempt in range(max_attempts):
        shuffled_players = shuffle_players(players_ordered)
        match_created = try_to_form_teams(request, club, shuffled_players)  # Pass request here

        if match_created:
            return True

    # If no valid match was created, try with the least played players
    return try_with_least_played(request, players_ordered)  # Pass request here



def shuffle_players(players_ordered):
    groups = {}
    for player in players_ordered:
        groups.setdefault(player.played_count, []).append(player)

    shuffled_players = []
    for count in sorted(groups.keys()):
        random.shuffle(groups[count])
        shuffled_players.extend(groups[count])
    
    return shuffled_players


def try_to_form_teams(request, club, shuffled_players):  # Accept request here
    for i in range(len(shuffled_players) - 3):
        candidate_group = shuffled_players[i:i + 4]
        if is_valid_group(candidate_group):
            return create_teams(request, club, candidate_group)  # Pass request here
    return False    


def is_valid_group(candidate_group):
    max_diff = max(p.played_count for p in candidate_group) - min(p.played_count for p in candidate_group)
    return max_diff <= 2


def create_teams(request, club, candidate_group):  # Accept request here
    team_pairings = [
        ((candidate_group[0], candidate_group[1]), (candidate_group[2], candidate_group[3])),
        ((candidate_group[0], candidate_group[2]), (candidate_group[1], candidate_group[3])),
        ((candidate_group[0], candidate_group[3]), (candidate_group[1], candidate_group[2])),
    ]
    random.shuffle(team_pairings)

    for team1_players, team2_players in team_pairings:
        team1, _ = Team.objects.get_or_create(
            player1=team1_players[0],
            player2=team1_players[1],
            club = club,
            defaults={'name': f"Team {team1_players[0].username} & {team1_players[1].username}"}
        )
        team2, _ = Team.objects.get_or_create(
            player1=team2_players[0],
            player2=team2_players[1],
            club = club,
            defaults={'name': f"Team {team2_players[0].username} & {team2_players[1].username}"}
        )

        if not Match.objects.filter(Q(team1=team1, team2=team2) | Q(team1=team2, team2=team1)).exists():
            Match.objects.create(team1=team1, team2=team2)
            messages.success(request, "New match created successfully!")  # Now this works
            return True

    return False


def try_with_least_played(request, players_ordered):  # Accept request here
    candidate_group = players_ordered[:4]
    return create_teams(request, candidate_group)  # Pass request here

@login_required
def club_matches(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    matches = Match.objects.filter(
        Q(team1__player1__club=club) | 
        Q(team1__player2__club=club) |
        Q(team2__player1__club=club) |
        Q(team2__player2__club=club)
    ).order_by('-created_at')
    
    return render(request, 'matches/club_matches.html', {'matches': matches, 'club': club})

def match_detail(request, club_id, match_id):
    match = get_object_or_404(Match, id=match_id)
    club = get_object_or_404(Club, id=club_id)
    team_winner_detail = get_object_or_404(TeamDetail, match=match, team=match.winner)
    team_loser_detail = get_object_or_404(TeamDetail, match=match, team=match.loser)
    return render(request, 'matches/match_detail.html', {'match': match, 'club': club, 'team_winner': team_winner_detail, 'team_loser': team_loser_detail})

def delete_match(request, club_id, match_id):
    match = get_object_or_404(Match, id=match_id)
    team_details = TeamDetail.objects.filter(match=match)
    if request.method == 'POST':
        for team in team_details:
            team.delete()
        match.delete()
        messages.success(request, "Match deleted successfully.")
        return redirect('club_matches', club_id=club_id)
    return render(request, 'matches/delete_match.html', {'match': match})

def edit_match(request, club_id, match_id):
    match = get_object_or_404(Match, id=match_id)
    teams = Team.objects.filter(club_id=club_id)
    if request.method == 'POST':
        # Update match details here if needed
        # For example, you might want to update team names or other attributes
        match.team1_score = request.POST.get('team1_score')
        match.team2_score = request.POST.get('team2_score')
        match.edit()
        
        return redirect('match_detail', club_id=club_id, match_id=match.id)
        pass  # Placeholder for actual update logic
    return render(request, 'matches/edit_match.html', {'match': match, 'club_id': club_id, 'teams': teams})

def calculate_expected_outcome(R, avg_rating):
    return 1 / (1 + 10 ** ((avg_rating - R) / 400))

def calculate_score_difference_factor(SA, SB):
    return 1 + abs(SA - SB) / (SA + SB)

def calculate_new_rating(W, E, K, FS):
    return K * (W - E) * FS

def calculate_k_stabilization(K_initial, n):
    return K_initial / (n ** 0.5)

def update_rating(R, STA, STB, W, avg_rating, K_initial, n):
    K = calculate_k_stabilization(K_initial, n)
    E = calculate_expected_outcome(R, avg_rating)
    FS = calculate_score_difference_factor(STA, STB)  # Assuming same score for simplicity
    return calculate_new_rating(W, E, K, FS)

def calculate_player_mmr_change(R, STA, STB, W, avg_rating, num_matches):
    # Placeholder for actual MMR change calculation logic
    K = 42
    return update_rating(R, STA, STB, W, avg_rating, K, num_matches)

def create_match(request, club_id):
    if request.method == 'POST':
        form = MatchCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Save the match, which now includes scores
                match = form.save(commit=True)  # Save the match, which now includes scores
                match.update_played()  # Update the match to set winner and loser
                
                # Create TeamDetail instances for winner and loser
                if match.winner and match.loser:
                    # Calculate average ratings for both teams
                    avg_rating_winner = match.winner.get_average_mmr()
                    avg_rating_loser = match.loser.get_average_mmr()
                    
                    winner_score = match.team1_score if match.winner == match.team1 else match.team2_score
                    loser_score = match.team2_score if match.winner == match.team1 else match.team1_score
                    
                    match_played_count_winner_player1 = match.winner.player1.matched_played_count
                    winner_player1_mmr_change= math.ceil(calculate_player_mmr_change(match.winner.player1.mmr, winner_score, loser_score, 1, avg_rating_loser, match_played_count_winner_player1))
                    
                    match_played_count_winner_player2 = match.winner.player2.matched_played_count
                    winner_player2_mmr_change = math.ceil(calculate_player_mmr_change(match.winner.player2.mmr, winner_score, loser_score, 1, avg_rating_loser, match_played_count_winner_player2))
                    
                    match_played_count_loser_player1 = match.loser.player1.matched_played_count
                    loser_player1_mmr_change = math.ceil(calculate_player_mmr_change(match.loser.player1.mmr, loser_score, winner_score, 0, avg_rating_winner, match_played_count_loser_player1))
                    
                    match_played_count_loser_player2 = match.loser.player2.matched_played_count
                    loser_player2_mmr_change = math.ceil(calculate_player_mmr_change(match.loser.player2.mmr, loser_score, winner_score, 0, avg_rating_winner, match_played_count_loser_player2))
                    
                    

                    # Create TeamDetail instances
                    TeamDetail.objects.create(
                        team=match.winner,
                        match=match,
                        player1_mmr_change=winner_player1_mmr_change,
                        player2_mmr_change=winner_player2_mmr_change
                    )
                    TeamDetail.objects.create(
                        team=match.loser,
                        match=match,
                        player1_mmr_change=loser_player1_mmr_change,
                        player2_mmr_change=loser_player2_mmr_change
                    )
                    
                
                messages.success(request, "Match created successfully.")
                return redirect('club_matches', club_id=club_id)
    else:
        form = MatchCreationForm()
    
    # Fetch teams associated with the club
    teams = Team.objects.filter(club_id=club_id)

    return render(request, 'matches/create_match.html', {'club_id': club_id, 'teams': teams, 'form': form})