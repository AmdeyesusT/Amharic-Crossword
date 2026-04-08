from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Puzzle
from .serializers import AdminCreatePuzzleSerializer, PuzzleListSerializer, PuzzleDetailSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .utils import generate_amharic_puzzle
from .models import WordBank

# Create your views here.
class PuzzleListView(generics.ListAPIView):
    """
    Returns a list of all Amharic puzzles. 
    Accessible to everyone (Read-Only).
    """
    queryset = Puzzle.objects.all().order_by('-created_at')
    serializer_class = PuzzleListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='difficulty', 
                description='Filter puzzles by difficulty (easy, medium, hard)', 
                required=False, 
                type=OpenApiTypes.STR
            ),
        ]
    )

    # Optional: Allow filtering by difficulty (e.g., ?difficulty=easy)
    def get_queryset(self):
        queryset = super().get_queryset()
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        return queryset

class PuzzleDetailView(generics.RetrieveAPIView):
    """
    Returns the full details and clues for a single puzzle.
    """
    queryset = Puzzle.objects.all()
    serializer_class = PuzzleDetailSerializer
    permission_class = [IsAuthenticatedOrReadOnly]


class AdminCreatePuzzleView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=AdminCreatePuzzleSerializer,
        responses={201: {"type": "object", "properties": {"message": {"type": "string"}}}}
    )
    def post(self, request):
        title = request.data.get('title')
        category_name = request.data.get('category') # e.g., 'History'
        count = request.data.get('word_count', 15)   # How many words to pull

        # 1. Fetch random words from your Word Bank
        words_from_bank = WordBank.objects.filter(
            category=category_name.upper()
        ).order_by('?')[:count] # '?' provides random ordering

        # 2. Convert database objects into the dictionary the generator needs
        # This creates: {'አበበ': 'የወንድ ስም', ...}
        word_data = {obj.word: [obj.clue_hint, obj.english_word] for obj in words_from_bank}

        if not word_data:
            return Response({"error": "No words found in this category"}, status=400)

        # 3. Pass the "pulled" data to the generator
        puzzle = generate_amharic_puzzle(title, word_data, user=request.user)
        
        return Response({"message": f"Puzzle '{puzzle.title}' created from Word Bank!"})