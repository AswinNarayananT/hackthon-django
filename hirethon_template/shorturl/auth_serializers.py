from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer, JWTSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomLoginSerializer(LoginSerializer):
    """Custom login serializer that returns access token in response body"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = self.authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class CustomJWTSerializer(JWTSerializer):
    """Custom JWT serializer that returns access token in response body"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = obj['user']
        return {
            'pk': user.pk,
            'email': user.email,
            'name': user.name,
        }


class CustomRegisterSerializer(RegisterSerializer):
    """Custom registration serializer"""
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data

    def get_cleaned_data(self):
        return {
            'name': self.validated_data.get('name', ''),
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
        }

    def save(self, request):
        cleaned_data = self.get_cleaned_data()
        user = User.objects.create_user(
            email=cleaned_data['email'],
            name=cleaned_data['name'],
            password=cleaned_data['password1']
        )
        return user
