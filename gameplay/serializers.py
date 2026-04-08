from rest_framework import serializers
from .models import UserProgress, Leaderboard

class SubmissionSerializer(serializers.Serializer):
    puzzle_id = serializers.IntegerField()
    time_spent = serializers.IntegerField(help_text="Time in seconds")
    # This expects a dictionary of clue_id: user_answer
    answers = serializers.DictField(
        child=serializers.CharField(), 
        help_text="Format: {'clue_id': 'አበበ'}"
    )

class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Leaderboard
        fields = ['username', 'puzzle_title', 'score', 'completion_time']