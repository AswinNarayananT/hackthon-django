from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from hirethon_template.users.models import User
from hirethon_template.users.api.serializers import UserSerializer, RegisterSerializer
from hirethon_template.shorturl.models import Organization, Membership

User = get_user_model()


class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)

        # Create tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        # Set refresh token in HTTP-only cookie
        response = Response({
            'access': access,
            'user': UserSerializer(user, context={'request': request}).data
        }, status=status.HTTP_200_OK)
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            samesite='Lax',  # adjust according to frontend domain
            secure=False  # set True in production HTTPS
        )
        return response


class CustomRefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token not found'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # Validate and refresh the token
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            # Get user from token payload
            user_id = refresh.payload.get('user_id')
            user = User.objects.get(id=user_id)
            
            # Return new access token
            response = Response({
                'access': access_token
            }, status=status.HTTP_200_OK)
            
            # Optionally rotate refresh token (recommended for security)
            new_refresh = RefreshToken.for_user(user)
            response.set_cookie(
                key='refresh_token',
                value=str(new_refresh),
                httponly=True,
                samesite='Lax',
                secure=False  # set True in production HTTPS
            )
            
            return response
            
        except TokenError as e:
            return Response(
                {'detail': 'Invalid or expired refresh token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class CustomRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Use transaction to ensure user and organization are created together
        try:
            with transaction.atomic():
                # Create user
                user = serializer.save()
                
                # Create default organization for the user
                org_name = f"{user.name}'s Organization" if user.name else f"{user.email.split('@')[0]}'s Organization"
                organization = Organization.objects.create(
                    name=org_name,
                    created_by=user
                )
                
                # Add user as admin member of the organization
                Membership.objects.create(
                    user=user,
                    organization=organization,
                    role='admin'
                )
                
                # Create tokens
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                
                # Set refresh token in HTTP-only cookie
                response = Response({
                    'access': access,
                    'user': UserSerializer(user, context={'request': request}).data
                }, status=status.HTTP_201_CREATED)
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    samesite='Lax',
                    secure=False  # set True in production HTTPS
                )
                return response
        except Exception as e:
            return Response(
                {'detail': f'Registration failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomLogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)
        # Clear the refresh token cookie
        response.delete_cookie('refresh_token')
        return response


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()
