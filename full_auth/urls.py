from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('djoser.urls')),  # Include default Djoser URLs
    path('api/', include('djoser.urls.jwt')),  # Include Djoser JWT URLs if needed
    path('api/', include('users.urls', namespace='auth')),  # Include custom URLs with namespace
]
