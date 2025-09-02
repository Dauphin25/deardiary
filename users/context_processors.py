from .models import UserProfile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Adjust if your related_name is different
        except UserProfile.DoesNotExist:
            profile = None
    else:
        profile = None
    return {
        'profile': profile
    }
