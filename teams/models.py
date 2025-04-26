from django.db import models, transaction

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, related_name='teams')
    
    player1 = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='teams_as_player1')
    player2 = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='teams_as_player2')
    times_played = models.IntegerField(default=0)  # Track number of times played
    wins = models.IntegerField(default=0)  # Track number of wins
    losses = models.IntegerField(default=0)  # Track number of losses
    average_mmr = models.IntegerField(default=0)  # Store average MMR in a field
    

    class Meta:
        unique_together = ('player1', 'player2')  # Ensure unique player combinations

    def save(self, *args, **kwargs):
        # Calculate average MMR of the team
        self.average_mmr = self.get_average_mmr()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.player1.username} & {self.player2.username})"
    
    def get_average_mmr(self):
        # Calculate the average MMR of the team members
        if self.player1 and self.player2:
            return (self.player1.mmr + self.player2.mmr) // 2
        return 0  # Return 0 if either player is not set
    

class TeamDetail(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='match_details')
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='team_details')
    player1_mmr_change = models.IntegerField(default=0)
    player2_mmr_change = models.IntegerField(default=0)

    date_recorded = models.DateTimeField(auto_now_add=True)
    
    def update_player_mmr(self, player, change):
        with transaction.atomic():
            """Update the player's MMR and ensure it doesn't go below zero."""
            if change > 0:
                player.wins += 1
            else:
                player.losses += 1
            player.mmr = max(player.mmr + change, 0)
            player.matched_played_count += 1  # Ensure matched_played_count is not None
            player.played_count += 1  # Increment played count
            player.save()

    def reverse_player_mmr(self, player, change):
        with transaction.atomic():
            if change > 0:
                player.wins -= 1
            else:
                player.losses -= 1
            player.mmr = max(player.mmr - change, 0)
            player.matched_played_count -= 1  # Ensure matched_played_count is not None
            player.played_count -= 1  # Increment played count
            player.save()
        
    
    def delete(self, *args, **kwargs):
        
        self.reverse_player_mmr(self.team.player1, self.player1_mmr_change)
        self.reverse_player_mmr(self.team.player2, self.player2_mmr_change)
        
        super().delete(*args, **kwargs)
            
    
    def save(self, *args, **kwargs):
        self.update_player_mmr(self.team.player1, self.player1_mmr_change)
        self.update_player_mmr(self.team.player2, self.player2_mmr_change)
        
        super().save(*args, **kwargs)
            
            

    def __str__(self):
        return f"Match Detail for {self.match}"