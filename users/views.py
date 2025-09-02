from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect  # For rendering templates and redirecting
from django.contrib.auth import login, authenticate, logout  # Auth-related helpers
from django.contrib.auth.decorators import login_required  # Restrict profile view to logged in users

from DiaryProject import settings
from diary.models import QuestionSet
from .forms import CustomUserCreationForm  # Our custom form
from .utils import get_limits

from django.shortcuts import redirect
from django.utils import translation


# Handle user registration
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Create form instance with POST data
        if form.is_valid():  # Check if form passes validation
            user = form.save()  # Save user to database
            login(request, user)  # Log the user in after registration
            return redirect('users:profile')  # Redirect to profile page
    else:
        form = CustomUserCreationForm()  # Empty form on GET

    return render(request, 'users/register.html', {'form': form})  # Render registration template

# Handle login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']  # Get username from form
        password = request.POST['password']  # Get password from form
        user = authenticate(request, username=username, password=password)  # Check credentials

        if user is not None:
            login(request, user)  # Log the user in
            return redirect('users:profile')  # Redirect to profile
        else:
            error = "Invalid username or password"
            return render(request, 'users/login.html', {'error': error})  # Return with error

    return render(request, 'users/login.html')  # GET request

# Handle logout
def logout_view(request):
    logout(request)  # Django built-in logout
    return redirect('pages:home')  # Redirect to homepage

# Show user profile (only for logged in users)
@login_required(login_url='users:login')
def profile_view(request):
    notifications_qs = request.user.notifications.all()

    # paginate with 10 per page
    paginator = Paginator(notifications_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    profile = request.user.userprofile
    limits = get_limits(request.user)
    current_qset_count = QuestionSet.objects.filter(owner=request.user).count()
    # Reset weekly answers if needed
    profile.reset_weekly_answers()

    context = {
        'profile': profile,
        'max_answers': limits['max_answers'],
        'max_qsets': limits['max_qsets'],
        'current_qset_count': current_qset_count,  # pass this to the template
        "page_obj": page_obj,  # for template pagination controls
        "next_reset": profile.next_reset,  # send datetime
    }
    return render(request, 'users/profile.html', context)
@login_required(login_url='users:login')
def upgrade_to_premium(request):
    profile = request.user.userprofile
    profile.plan = 'premium'
    profile.save()
    messages.success(request, "You’ve been upgraded to Premium!")
    return redirect('users:profile')  # adjust if your profile URL name is different

def set_language(request, lang_code):
    if lang_code not in dict(settings.LANGUAGES):
        lang_code = settings.LANGUAGE_CODE
    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    return redirect(request.META.get('HTTP_REFERER', '/'))