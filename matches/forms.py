from .models import Match
from django import forms

class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_score', 'team2_score']

    def clean(self):
        cleaned_data = super().clean()
        team1_score = cleaned_data.get("team1_score")
        team2_score = cleaned_data.get("team2_score")

        if team1_score < 0 or team2_score < 0:
            raise forms.ValidationError("Scores cannot be negative.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Additional logic can be added here if needed
        if commit:
            instance.save()
        return instance

    
class MatchCreationForm(forms.ModelForm):
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
    