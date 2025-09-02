from django import forms  # For form building
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # Built-in forms
from .models import CustomUser  # Import the custom user model

# Custom registration form
class CustomUserCreationForm(UserCreationForm):
    # Define all fields visible on the registration page
    name = forms.CharField(max_length=50)
    surname = forms.CharField(max_length=50)
    city = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser  # Connect the form to our user model
        fields = ['username', 'email', 'name', 'surname', 'city', 'phone_number', 'password1', 'password2']
