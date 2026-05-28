from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from diary.models import QuestionSet
from .forms import CustomUserCreationForm
from .utils import get_limits


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'users:profile')
            return redirect(next_url)
        return render(request, 'users/login.html', {'error': "Invalid username or password"})
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('pages:home')


@login_required(login_url='users:login')
def profile_view(request):
    profile = request.user.userprofile
    profile.reset_weekly_answers()

    notifications_qs = request.user.notifications.select_related('actor', 'question_set').all()
    paginator = Paginator(notifications_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    limits = get_limits(request.user)
    current_qset_count = QuestionSet.objects.filter(owner=request.user).count()

    return render(request, 'users/profile.html', {
        'profile': profile,
        'max_answers': limits['max_answers'],
        'max_qsets': limits['max_qsets'],
        'current_qset_count': current_qset_count,
        'page_obj': page_obj,
        'next_reset': profile.next_reset,
    })


@login_required(login_url='users:login')
def upgrade_to_premium(request):
    profile = request.user.userprofile
    profile.plan = 'premium'
    profile.save()
    messages.success(request, "You've been upgraded to Premium!")
    return redirect('users:profile')
