from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
from drf_spectacular.utils import extend_schema
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class RegisterView(APIView):
    @extend_schema(request=RegisterSerializer, responses={201: RegisterSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        # 1. This one line replaces all your manual 'if not email' checks
        if serializer.is_valid():
            # 2. Save the user (using the logic we put in the serializer)
            user = serializer.save()
            
            # 3. Create the profile
            Profile.objects.create(user=user)
            
            # 4. Return the tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        # 5. If data is bad (e.g. invalid Amharic characters or short password), 
        # it returns the exact error message automatically
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    """
    Takes email and password, returns JWT Access and Refresh tokens 
    plus user details.
    """
    serializer_class = MyTokenObtainPairSerializer
    @extend_schema(
        request=MyTokenObtainPairSerializer,
        responses={200: MyTokenObtainPairSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)