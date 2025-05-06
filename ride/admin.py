from django.contrib import admin
from .models import Booking, Review

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'ride_type', 'rider', 'driver', 'pickup_location',
        'pickup_date', 'pickup_time', 'status', 'get_total_price'
    ]
    list_filter = ['status', 'ride_type', 'created_at', 'vehicle_type']
    search_fields = ['rider__user__username', 'driver__user__username', 'pickup_location', 'drop_location']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'rating', 'comment', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['booking__rider__user__username', 'booking__driver__user__username', 'comment']
