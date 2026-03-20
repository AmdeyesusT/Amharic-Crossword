from django.db import models
from django.conf import settings

class UserProgress(models.Model):
    """Tracks a Lazy User's current typed letters in an active puzzle."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puzzle = models.ForeignKey('puzzles.Puzzle', on_delete=models.CASCADE)
    
    current_state = models.JSONField(default=dict)
    
    is_completed = models.BooleanField(default=False)
    time_spent = models.PositiveIntegerField(default=0, help_text="Time in seconds")
    last_played = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'puzzle') # One progress record per user per puzzle

class Leaderboard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puzzle = models.ForeignKey('puzzles.Puzzle', on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    completion_time = models.PositiveIntegerField()
    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', 'completion_time']