from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Driver, Vehicle
from django.contrib.auth import login
from core.forms import DriverRegistrationForm

def register(request):
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Driver account created successfully!')
            return redirect('driver:dashboard')
    else:
        form = DriverRegistrationForm()
    return render(request, 'driver/register.html', {'form': form})

@login_required
def dashboard(request):
    try:
        driver = request.user.driver
        current_bookings = driver.bookings.filter(
            status__in=['pending', 'confirmed']
        ).order_by('pickup_date', 'pickup_time')
        
        context = {
            'driver': driver,
            'current_bookings': current_bookings,
            'total_trips': driver.total_trips,
            'total_earnings': driver.total_earnings,
            'rating': driver.rating,
            'is_available': driver.is_available
        }
        
        try:
            vehicle = Vehicle.objects.get(driver=driver, is_active=True)
            context['vehicle'] = vehicle
        except Vehicle.DoesNotExist:
            messages.warning(request, 'No active vehicle found. Please update your vehicle information.')
        
        return render(request, 'driver/dashboard.html', context)
        
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('home')

@login_required
def profile(request):
    try:
        driver = request.user.driver
        if request.method == 'POST':
            driver.is_available = request.POST.get('is_available') == 'on'
            driver.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('driver:dashboard')
        return render(request, 'driver/profile.html', {'driver': driver})
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('home')

@login_required
def bookings(request):
    try:
        driver = request.user.driver
        context = {
            'pending_bookings': driver.bookings.filter(status='pending').order_by('pickup_date', 'pickup_time'),
            'confirmed_bookings': driver.bookings.filter(status='confirmed').order_by('pickup_date', 'pickup_time'),
            'completed_bookings': driver.bookings.filter(status='completed').order_by('-pickup_date', '-pickup_time')[:10]
        }
        return render(request, 'driver/bookings.html', context)
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('home')

@login_required
def vehicle_info(request):
    try:
        driver = request.user.driver
        vehicles = Vehicle.objects.filter(driver=driver)
        return render(request, 'driver/vehicle.html', {'vehicles': vehicles})
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('home')
