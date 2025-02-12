from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Club(AbstractUser):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_club = models.BooleanField(default=True)

    # Add unique related_name for groups and user_permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this club belongs to. A club will get all permissions granted to each of its groups.',
        related_name="club_groups",  # Unique related_name
        related_query_name="club",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this club.',
        related_name="club_user_permissions",  # Unique related_name
        related_query_name="club",
    )

    def __str__(self):
        return self.name

class User(AbstractUser):
    # MMR choices
    BEGINNER = 800
    INTERMEDIATE = 1500
    PROFESSIONAL = 2200
    MMR_CHOICES = [
        (BEGINNER, 'Beginner (800 MMR)'),
        (INTERMEDIATE, 'Intermediate (1500 MMR)'),
        (PROFESSIONAL, 'Professional (2200 MMR)'),
    ]

    # Fields
    club = models.ForeignKey('Club', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    mmr = models.IntegerField(choices=MMR_CHOICES, default=BEGINNER)
    is_user = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)  # Track online status
    played_count = models.IntegerField(default=0)

    # Add unique related_name for groups and user_permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of its groups.',
        related_name="user_groups",  # Unique related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_user_permissions",  # Unique related_name
        related_query_name="user",
    )

    def __str__(self):
        return self.username

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    player1 = models.ForeignKey('User', on_delete=models.CASCADE, related_name='teams_as_player1')
    player2 = models.ForeignKey('User', on_delete=models.CASCADE, related_name='teams_as_player2')
    average_mmr = models.IntegerField(default=0)

    class Meta:
        unique_together = ('player1', 'player2')  # Ensure unique player combinations

    def save(self, *args, **kwargs):
        # Calculate average MMR of the team
        self.average_mmr = (self.player1.mmr + self.player2.mmr) // 2
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.player1.username} & {self.player2.username})"
    
class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_won', null=True, blank=True)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team1} vs {self.team2}"