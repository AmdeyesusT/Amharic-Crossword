from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# accounts/serializers.py
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        # Use create_user to handle password hashing automatically
        return User.objects.create_user(**validated_data)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims (data hidden inside the token)
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # This part runs when the user submits their email/password
        data = super().validate(attrs)
        
        # Add extra data to the plain-text JSON response
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data