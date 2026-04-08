from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics # Added generics here
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404 # Fixed typo here
from puzzles.models import Puzzle
from .models import UserProgress, Leaderboard
from .serializers import SubmissionSerializer, LeaderboardSerializer
from drf_spectacular.utils import extend_schema
from django.db.models import Sum

# Create your views here.
class SubmitPuzzleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves the player's saved state for a specific puzzle.
        """
        puzzle_id = request.query_params.get('puzzle_id')
        if not puzzle_id:
            return Response({"error": "puzzle_id is required"}, status=400)

        # Look for existing progress
        progress = UserProgress.objects.filter(
            user=request.user, 
            puzzle_id=puzzle_id
        ).first()

        if not progress:
            return Response({
                "message": "New game",
                "time_spent": 0,
                "answers": {},
                "is_completed": False
            }, status=200)

        return Response({
            "message": "Resuming game",
            "time_spent": progress.time_spent,
            "answers": progress.current_state,
            "is_completed": progress.is_completed,
            "score": progress.score
        }, status=200)
    
    @extend_schema(
        request=SubmissionSerializer,
        responses={200: {
            "type": "object",
            "properties": {
                "is_completed": {"type": "boolean"},
                "score_earned": {"type": "integer"}
            }
        }},
        description="Submit answers for an Amharic puzzle. Answers should be clue_id: word."
    )
    def post(self, request):
        serializer = SubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Use the fixed shortcut here
        puzzle_id = get_object_or_404(Puzzle, id=serializer.validated_data['puzzle_id'])
        new_answers = serializer.validated_data['answers']
        session_time = serializer.validated_data['time_spent']

        # 1. Fetch current progress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user, 
            puzzle_id=puzzle_id,
            defaults={'answers_data': {}, 'time_spent': 0}
        )

        # 2. MERGE: Keep old answers, update with new ones
        updated_answers = progress.current_state
        updated_answers.update(new_answers) 

        # 3. ACCUMULATE TIME: Total time = Old time + This session's time
        total_time_spent = progress.time_spent + session_time

        # 4. GRADE the MERGED answers
        correct_count = 0
        clues = Puzzle.objects.get(id=puzzle_id).clues.all()
        
        # 1. Grade the Puzzle
        for clue in clues:
            # We convert clue.id to string because JSON keys are always strings
            answer_in_storage = updated_answers.get(str(clue.id))
            # Clean up whitespace for Amharic strings to avoid "hidden" errors
            if answer_in_storage:
                # Clean strings: Remove spaces and ensure lowercase if any English is mixed in
                clean_submitted = answer_in_storage.strip()
                clean_correct = clue.answer.strip()
                
                if clean_submitted == clean_correct:
                    correct_count += 1

        is_completed = (correct_count == clues.count())
        score = correct_count * 10
        
        # 5. SAVE the complete state back to the DB
        progress.answers_data = updated_answers
        progress.time_spent = total_time_spent
        progress.score = score
        progress.is_completed = is_completed
        progress.save()

        base_score = score
        time_penalty = int(total_time_spent / 30) # 1 point off every 30 seconds
        final_score = max(0, base_score - time_penalty)

        # 3. If finished, add to Leaderboard
        if is_completed:
            leaderboard_entry, created = Leaderboard.objects.get_or_create(
                user=request.user, 
                puzzle=puzzle_id,
                defaults={'score': final_score, 'completion_time': total_time_spent}
            )
    
            # If they already existed, check if this new time is FASTER
            if not created:
                if total_time_spent < leaderboard_entry.completion_time:
                    leaderboard_entry.completion_time = total_time_spent
                    leaderboard_entry.score = final_score
                    leaderboard_entry.save()
                    is_new_record = True
                else:
                    is_new_record = False
            else:
                is_new_record = True
        else:
            is_new_record = False

        return Response({
            "is_completed": is_completed,
            "total_time": total_time_spent,
            "score_earned": score,
            "is_new_record": is_new_record
        }, status=status.HTTP_200_OK)
    

class GlobalLeaderboardView(generics.ListAPIView):
    """
    Returns users ranked by their TOTAL score across all puzzles.
    """
    serializer_class = LeaderboardSerializer
    # Leaderboards are usually public, so we allow read access to everyone

    def get_queryset(self):
        # This sums up all scores for each user and ranks them
        return Leaderboard.objects.values('user__username')\
            .annotate(total_score=Sum('score'))\
            .order_by('-total_score')[:50]