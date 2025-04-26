from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
# Create your models here.

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