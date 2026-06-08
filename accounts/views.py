from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    """Authentication endpoints: register, login, logout, me."""

    def get_serializer_class(self):
        if self.action == 'register':
            return RegisterSerializer
        if self.action == 'login':
            return LoginSerializer
        if self.action == 'logout':
            return LogoutSerializer
        if self.action == 'me':
            return UserProfileSerializer
        return RegisterSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'User registered successfully'},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )

        if not user:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def logout(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return Response(
                {'message': 'Logged out successfully'},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {'detail': 'Invalid refresh token'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
