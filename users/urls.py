from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    RegisterUserView,
    LogoutView
)

app_name = 'auth'  # Namespace for the app

urlpatterns = [
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('jwt/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
