from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only serializer for the authenticated user's profile."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id', 'username', 'email')


class LoginSerializer(serializers.Serializer):
    """Serializer for login credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout (refresh token blacklisting)."""

    refresh = serializers.CharField()
