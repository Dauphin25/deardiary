from django.urls import path  # For defining routes
from . import views  # Import our views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),  # Registration page
    path('login/', views.login_view, name='login'),  # Login page
    path('logout/', views.logout_view, name='logout'),  # Logout function
    path('profile/', views.profile_view, name='profile'),  # Profile page
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('upgrade/', views.upgrade_to_premium, name='upgrade_to_premium'),
]
