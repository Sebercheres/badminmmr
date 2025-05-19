from .models import Match
from django import forms
from accounts.models import User
from teams.models import Team
from django.core.exceptions import ValidationError
class MatchResultForm(forms.ModelForm):
    team1_score = forms.IntegerField(required=True, label="Team 1 Score")
    team2_score = forms.IntegerField(required=True, label="Team 2 Score")

    class Meta:
        model = Match
        fields = ['team1', 'team2', 'team1_score', 'team2_score']

    def clean(self):
        cleaned_data = super().clean()
        team1 = cleaned_data.get("team1")
        team2 = cleaned_data.get("team2")

        if team1 == team2:
            raise forms.ValidationError("Teams cannot be the same.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set scores from the form
        instance.team1_score = self.cleaned_data.get('team1_score')
        instance.team2_score = self.cleaned_data.get('team2_score')
        
        if commit:  
            instance.save()
        return instance

class MatchCreationForm(forms.ModelForm):
    team1_player1 = forms.ModelChoiceField(queryset=User .objects.none(), required=True, label="Team 1 Player 1")
    team1_player2 = forms.ModelChoiceField(queryset=User .objects.none(), required=True, label="Team 1 Player 2")
    team2_player1 = forms.ModelChoiceField(queryset=User .objects.none(), required=True, label="Team 2 Player 1")
    team2_player2 = forms.ModelChoiceField(queryset=User .objects.none(), required=True, label="Team 2 Player 2")
    team1_score = forms.IntegerField(required=True, label="Team 1 Score")
    team2_score = forms.IntegerField(required=True, label="Team 2 Score")

    class Meta:
        model = Match
        fields = ['team1_player1', 'team1_player2', 'team2_player1', 'team2_player2', 'team1_score', 'team2_score']

    def __init__(self, *args, **kwargs):
        club = kwargs.pop('club', None)
        super().__init__(*args, **kwargs)
        if club:
            players_qs = User.objects.filter(club=club, is_active=True)
            self.fields['team1_player1'].queryset = players_qs
            self.fields['team1_player2'].queryset = players_qs
            self.fields['team2_player1'].queryset = players_qs
            self.fields['team2_player2'].queryset = players_qs

    def clean(self):
        cleaned_data = super().clean()
        t1_p1 = cleaned_data.get("team1_player1")
        t1_p2 = cleaned_data.get("team1_player2")
        t2_p1 = cleaned_data.get("team2_player1")
        t2_p2 = cleaned_data.get("team2_player2")

        if not all([t1_p1, t1_p2, t2_p1, t2_p2]):
            raise ValidationError("All four players must be selected.")

        if t1_p1 == t1_p2:
            raise ValidationError("Team 1 players cannot be the same.")

        if t2_p1 == t2_p2:
            raise ValidationError("Team 2 players cannot be the same.")

        # Check for players overlapping between teams
        team1_players = {t1_p1, t1_p2}
        team2_players = {t2_p1, t2_p2}
        if team1_players.intersection(team2_players):
            raise ValidationError("A player cannot be on both teams.")

        return cleaned_data

    def _get_or_create_team(self, player_a, player_b):
        """Return existing team with these two players regardless of order, or create a new one."""
        team, created = Team.objects.get_or_create(
            player1=player_a,
            player2=player_b,
            defaults={'name': f"{player_a.username} & {player_b.username}", 'club': player_a.club}
        )
        return team

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.team1_score = self.cleaned_data.get('team1_score')
        instance.team2_score = self.cleaned_data.get('team2_score')

        # Get or create team1
        team1 = self._get_or_create_team(self.cleaned_data['team1_player1'], self.cleaned_data['team1_player2'])

        # Get or create team2
        team2 = self._get_or_create_team(self.cleaned_data['team2_player1'], self.cleaned_data['team2_player2'])

        instance.team1 = team1
        instance.team2 = team2

        if commit:
            instance.save()
        return instance
