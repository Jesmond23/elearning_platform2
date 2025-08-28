from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from dashboard.api import current_user_api 


#Swagger
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

def homepage(request):
     return render(request, 'home.html')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', homepage),
    path('dashboard/', include('dashboard.urls')),
    path('courses/', include('courses.urls')),

    path('chat/', include('chat.urls')),

    path('api/user/', current_user_api, name='user_api'),
  
    # OpenAPI schema (JSON)
path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

# Swagger UI
path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

# ReDoc UI
path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),


#API for participants in course
path('courses/', include('courses.urls')),


] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
