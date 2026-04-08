from django.urls import path
from .views import LoginView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    # This allows the frontend to get a new Access Token using a Refresh Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]