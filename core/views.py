from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Driver, Vehicle
from django.contrib.auth.models import User
from .forms import RiderRegistrationForm, DriverRegistrationForm
from django.contrib.auth import login

def home(request):
    if request.user.is_authenticated:
        try:
            # Check if user is a driver
            driver = request.user.driver
            return redirect('driver:dashboard')
        except Driver.DoesNotExist:
            # User is a rider or other type
            return render(request, 'core/home.html')
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = RiderRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = RiderRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def driver_register(request):
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in automatically
            messages.success(request, 'Driver account created successfully!')
            return redirect('driver:dashboard')
    else:
        form = DriverRegistrationForm()
    return render(request, 'core/driver_register.html', {'form': form})

@login_required
def profile(request):
    if hasattr(request.user, 'rider'):
        user_profile = request.user.rider
    elif hasattr(request.user, 'driver'):
        user_profile = request.user.driver
    else:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    if request.method == 'POST':
        user_profile.phone_number = request.POST.get('phone_number')
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'core/profile.html', {'profile': user_profile})
