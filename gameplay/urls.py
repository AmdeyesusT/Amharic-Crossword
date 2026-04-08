from django.urls import path
from .views import SubmitPuzzleView, GlobalLeaderboardView

urlpatterns = [
    # POST /api/gameplay/submit/
    path('', SubmitPuzzleView.as_view(), name='submit-puzzle'),
    
    # GET /api/gameplay/leaderboard/
    path('', GlobalLeaderboardView.as_view(), name='global-leaderboard'),
]