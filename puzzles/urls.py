from django.urls import path
from .views import AdminCreatePuzzleView, PuzzleListView, PuzzleDetailView

urlpatterns = [
    path('', PuzzleListView.as_view(), name='puzzle-list'),
    path('<int:pk>/', PuzzleDetailView.as_view(), name='puzzle-detail'),
    path('admin-create/', AdminCreatePuzzleView.as_view(), name='admin-create-puzzle'),
]