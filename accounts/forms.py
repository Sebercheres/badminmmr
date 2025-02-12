from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Club, User, Match

# Club Registration Form
class ClubRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True, help_text="Club Name")
    description = forms.CharField(widget=forms.Textarea, required=False, help_text="Club Description")

    class Meta:
        model = Club
        fields = ['username', 'name', 'description', 'password1', 'password2']

# User Registration Form
class UserRegistrationForm(UserCreationForm):
    mmr = forms.ChoiceField(choices=User.MMR_CHOICES, required=True, help_text="Select your initial MMR")

    class Meta:
        model = User
        fields = ['username', 'mmr', 'password1', 'password2']

# Club Selection Form
class ClubSelectionForm(forms.Form):
    club = forms.ModelChoiceField(queryset=Club.objects.all(), required=True, help_text="Select a Club")

# Match Result Form
class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_score', 'team2_score']