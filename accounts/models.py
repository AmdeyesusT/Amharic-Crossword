from django.db import models
from django.contrib.auth.models import AbstractUser
from gameplay.models import Leaderboard

class User(AbstractUser):
    AUTH_CHOICES = [
        ('local', 'Email/Password'),
        ('google', 'Google OAuth'),
        ('apple', 'Apple OAuth'),
    ]

    email = models.EmailField(unique=True)
    auth_type = models.CharField(
        max_length=20, 
        choices=AUTH_CHOICES, 
        default='local'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['']

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    @property
    def total_points(self):
        """Calculates total points from the Leaderboard table on demand."""
        # This sums up every score row for this specific user
        return Leaderboard.objects.filter(user=self.user).aggregate(Sum('score'))['score__sum'] or 0
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.email}"