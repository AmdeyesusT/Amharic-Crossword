from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

User = get_user_model()

class GuestUserCreateView(APIView):
    """
    Step 1: Create a 'Shadow User' when a guest first lands on the site.
    """
    def post(self, request):
        random_id = str(uuid.uuid4())[:8]
        username = f"guest_{random_id}"
        
        user = User.objects.create(
            username=username,
            is_guest=True,
            auth_type='local'
        )
        from .models import Profile
        Profile.objects.create(user=user)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'is_guest': user.is_guest
        }, status=status.HTTP_201_CREATED)

class ConvertGuestToMemberView(APIView):
    """
    Step 2: Upgrade a Guest to a Full Member without losing their Amharic progress.
    """
    def post(self, request):
        user = request.user
        
        if not user.is_authenticated or not user.is_guest:
            return Response({"error": "Only guests can convert to members."}, status=400)

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=400)

        user.email = email
        user.set_password(password)
        user.is_guest = False
        user.save()

        return Response({"message": "Successfully upgraded to a full account!"}, status=200)