from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from .serializers import UserSerializer

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        
        # Check if email or phone is provided
        if not data.get('email') and not data.get('phone'):
            return Response(
                {"error": "Either email or phone is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Hash the password
        if 'password' in data:
            data['password'] = make_password(data['password'])
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "user": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)