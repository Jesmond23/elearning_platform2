from django.urls import path
from .views import register_view, profile_view, edit_profile, public_profile
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', LoginView.as_view(template_name = 'accounts/login.html'), name='login'),
    path('logout/',LogoutView.as_view(next_page='login'),name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile, name= 'edit_profile'),
    path('view/<int:user_id>/course/<int:course_id>/', public_profile, name='public_profile'),
    # Public profile with optional course context
    path('view/<int:user_id>/', views.public_profile_simple, name='public_profile_simple'),

    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]