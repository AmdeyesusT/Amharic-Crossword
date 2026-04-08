from rest_framework import serializers
from .models import Puzzle, Clue

class ClueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clue
        fields = ['id', 'puzzle', 'clue_text', 'answer', 'x_coord', 'y_coord', 'direction']

class PuzzleListSerializer(serializers.ModelSerializer):
    """Simplified version for the selection menu"""
    class Meta:
        model = Puzzle
        fields = ['id', 'title', 'difficulty', 'grid_data', 'created_at']

class PuzzleDetailSerializer(serializers.ModelSerializer):
    """Full version including all clues for the game board"""
    clues = ClueSerializer(many=True, read_only=True)

    class Meta:
        model = Puzzle
        fields = ['id', 'title', 'difficulty', 'grid_data', 'clues']

class AdminCreatePuzzleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, help_text="Title of the puzzle")
    category = serializers.CharField(max_length=50, help_text="Category name from WordBank")
    word_count = serializers.IntegerField(default=15, help_text="Number of words to pull")