from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

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
    club = models.ForeignKey('clubs.Club', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    mmr = models.IntegerField(choices=MMR_CHOICES, default=BEGINNER)
    is_user = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)  # Track online status
    played_count = models.IntegerField(default=0)
    matched_played_count = models.IntegerField(default=1)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    

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