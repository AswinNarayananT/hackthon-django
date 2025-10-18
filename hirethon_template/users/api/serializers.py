from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from hirethon_template.users.models import User as UserType


User = get_user_model()


class UserSerializer(serializers.ModelSerializer[UserType]):
    class Meta:
        model = User
        fields = ["id", "email", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class RegisterSerializer(serializers.ModelSerializer[UserType]):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm Password')

    class Meta:
        model = User
        fields = ["email", "name", "password", "password2"]

    def validate_password(self, value):
        # Validate password using Django's password validators
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        # Create user without password first
        user = User(
            email=validated_data['email'],
            name=validated_data.get('name', '')
        )
        # Use set_password to properly hash the password
        user.set_password(validated_data['password'])
        user.save()
        return user
