from django.contrib import admin
from .models import Rider, Driver, Vehicle

@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'total_rides', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('gender', 'created_at')
    readonly_fields = ('total_rides', 'created_at', 'updated_at')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'rating', 'is_available', 'total_trips', 'document_verified')
    list_filter = ('is_available', 'document_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'license_number', 'phone_number')
    readonly_fields = ('rating', 'total_trips', 'total_earnings', 'created_at', 'updated_at')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('model', 'vehicle_number', 'vehicle_type', 'driver', 'capacity', 'ac_available', 'is_active')
    list_filter = ('vehicle_type', 'ac_available', 'is_active')
    search_fields = ('vehicle_number', 'model', 'driver__user__username')
