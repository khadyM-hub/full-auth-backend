from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.core.mail import send_mail
from botocore.exceptions import ClientError
import logging
from django.contrib.auth.models import User
from .models import UserAccount

# Initialize logger for error handling
logger = logging.getLogger(__name__)



# Helper function to send verification email and handle SES errors

def send_verification_email(user):
    """
    This function sends a verification email to the user and handles SES unverified email errors.
    """
    try:
        subject = "Verify your email address"
        message = f"Click the link to verify your email: http://yourdomain.com/verify/{user.id}"
        recipient_list = [user.email]
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    
    except ClientError as e:
        error_message = str(e)
        if "Address is not verified" in error_message:
            logger.error(f"SES email verification failed: {error_message}")
            # Optional: Notify the user or handle it in your own way
        else:
            logger.error(f"Error sending email: {error_message}")
            raise e  # Raise other exceptions for further handling


# Custom token views (remain unchanged)
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response
    

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response
    

class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)

# Logout view to clear access and refresh tokens (remains unchanged)
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response

# New user registration view with SES email handling

class RegisterUserView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        # Create the user
        try:
            user = UserAccount.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        except Exception as e:
            return Response({"message": "User creation failed"}, status=status.HTTP_400_BAD_REQUEST)

        # Send verification email
        try:
            send_verification_email(user)
            return Response({"message": "User created successfully. Verification email sent."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return Response({"message": "User created but failed to send verification email."}, status=status.HTTP_201_CREATED)

