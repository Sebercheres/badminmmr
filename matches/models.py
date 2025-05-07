from django.db import models
from teams.models import Team
from django.db import transaction

# Create your models here.
class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_won', null=True, blank=True)
    loser = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_lost', null=True, blank=True)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def update_played(self, *args, **kwargs):
        # Update times played and wins/losses
        with transaction.atomic():
            self.team1.times_played += 1
            self.team2.times_played += 1
            if self.winner == self.team1:
                self.team1.wins += 1
                self.team2.losses += 1
            elif self.winner == self.team2:
                self.team2.wins += 1
                self.team1.losses += 1

            # Save the team instances to persist changes
            self.team1.save()
            self.team2.save()

        

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Determine winner and loser based on scores
            if self.team1_score > self.team2_score:
                self.winner = self.team1
                self.loser = self.team2
            elif self.team2_score > self.team1_score:
                self.winner = self.team2
                self.loser = self.team1
            else:
                self.winner = None
                self.loser = None  # Handle draw case if needed

            
            super().save(*args, **kwargs)
    
            
    def delete(self, *args, **kwargs):
        with transaction.atomic():
            # Update times played and wins/losses
            self.team1.times_played -= 1
            self.team2.times_played -= 1
            if self.winner == self.team1:
                self.team1.wins -= 1
                self.team2.losses -= 1
            elif self.winner == self.team2:
                self.team2.wins -= 1
                self.team1.losses -= 1
            # Save the team instances to persist changes
            self.team1.save()
            self.team2.save()

            super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.team1} vs {self.team2}"
    
