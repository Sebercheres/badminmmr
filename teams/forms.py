from django import forms
from .models import Team

class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'player1', 'player2']  # Include the fields you want in the form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter team name'})
        self.fields['player1'].widget.attrs.update({'placeholder': 'Enter player1 username'})
        self.fields['player2'].widget.attrs.update({'placeholder': 'Enter player2 username'})