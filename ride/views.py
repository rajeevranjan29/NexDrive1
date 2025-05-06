from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.conf import settings
from .models import Booking, Review
from core.models import Driver
from django.utils import timezone
from .forms import BookingForm, ReviewForm
from django.http import JsonResponse

@login_required
def create_booking(request):
    ride_type = request.GET.get('type', 'outstation')  # Default to outstation if no type specified
    
    if request.method == 'POST':
        form = BookingForm(request.POST, ride_type=request.POST.get('ride_type'))
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.rider = request.user.rider
                booking.ride_type = request.POST.get('ride_type')
                
                # Save coordinates and distance
                booking.pickup_lat = form.cleaned_data.get('pickup_lat')
                booking.pickup_lng = form.cleaned_data.get('pickup_lng')
                booking.drop_lat = form.cleaned_data.get('drop_lat')
                booking.drop_lng = form.cleaned_data.get('drop_lng')
                booking.distance = form.cleaned_data.get('distance')
                
                # Validate required fields based on ride type
                if booking.ride_type == 'airport' and not booking.flight_number:
                    raise ValueError('Flight number is required for airport transfers')
                elif booking.ride_type == 'rental':
                    rental_hours = form.cleaned_data.get('rental_hours')
                    if not rental_hours or rental_hours < 2 or rental_hours > 12:
                        raise ValueError('Rental hours must be between 2 and 12')
                elif booking.ride_type == 'outstation':
                    if not booking.drop_location:
                        raise ValueError('Drop location is required for outstation trips')
                    if not booking.return_date:
                        raise ValueError('Return date is required for outstation trips')
                    if booking.return_date < booking.pickup_date:
                        raise ValueError('Return date must be after pickup date')
                
                booking.save()
                messages.success(request, 'Your booking has been created successfully!')
                return redirect('ride:booking_list')
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'An error occurred while creating your booking: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = BookingForm(ride_type=ride_type)
    
    return render(request, 'ride/create_booking.html', {
        'form': form,
        'ride_type': ride_type,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })

@login_required
def booking_list(request):
    if hasattr(request.user, 'rider'):
        bookings = request.user.rider.bookings.all()
    elif hasattr(request.user, 'driver'):
        bookings = request.user.driver.trips.all()
    else:
        bookings = []
    return render(request, 'ride/booking_list.html', {'bookings': bookings})

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if not (hasattr(request.user, 'rider') and request.user.rider == booking.rider) and \
       not (hasattr(request.user, 'driver') and request.user.driver == booking.driver):
        messages.error(request, "You don't have permission to view this booking.")
        return redirect('ride:booking_list')
    return render(request, 'ride/booking_detail.html', {'booking': booking})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if not hasattr(request.user, 'rider') or request.user.rider != booking.rider:
        messages.error(request, "You don't have permission to cancel this booking.")
        return redirect('ride:booking_list')
    
    if booking.status != 'PENDING':
        messages.error(request, "Only pending bookings can be cancelled.")
        return redirect('ride:booking_detail', pk=pk)
    
    if request.method == 'POST':
        booking.status = 'CANCELLED'
        booking.cancellation_reason = request.POST.get('reason', '')
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('ride:booking_list')
    
    return render(request, 'ride/cancel_booking.html', {'booking': booking})

@login_required
def create_review(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk)
    if not hasattr(request.user, 'rider') or request.user.rider != booking.rider:
        messages.error(request, "You don't have permission to review this booking.")
        return redirect('ride:booking_list')
    
    if booking.status != 'COMPLETED':
        messages.error(request, "You can only review completed rides.")
        return redirect('ride:booking_detail', pk=booking_pk)
    
    if hasattr(booking, 'review'):
        messages.error(request, "You have already reviewed this booking.")
        return redirect('ride:booking_detail', pk=booking_pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            
            # Update driver's rating
            driver = booking.driver
            total_reviews = Review.objects.filter(booking__driver=driver).count()
            avg_rating = Review.objects.filter(booking__driver=driver).aggregate(models.Avg('rating'))['rating__avg']
            driver.rating = round(avg_rating, 2)
            driver.save()
            
            messages.success(request, "Thank you for your review!")
            return redirect('ride:booking_detail', pk=booking_pk)
    else:
        form = ReviewForm()
    
    return render(request, 'ride/create_review.html', {'form': form, 'booking': booking})

@login_required
def review_list(request):
    if hasattr(request.user, 'rider'):
        reviews = Review.objects.filter(booking__rider=request.user.rider)
    elif hasattr(request.user, 'driver'):
        reviews = Review.objects.filter(booking__driver=request.user.driver)
    else:
        reviews = []
    return render(request, 'ride/review_list.html', {'reviews': reviews})
