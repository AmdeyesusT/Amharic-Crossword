from django.db import models
from django.contrib.auth.models import AbstractUser

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
    is_guest = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    total_points = models.PositiveIntegerField(default=0)
    all_time_rank = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.email}"