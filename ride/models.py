from django.db import models
from django.utils import timezone
from core.models import Rider, Driver, Vehicle

class Booking(models.Model):
    RIDE_TYPES = [
        ('airport', 'Airport Transfer'),
        ('rental', 'Hourly Rental'),
        ('outstation', 'Outstation'),
    ]

    VEHICLE_TYPES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('luxury', 'Luxury'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    AIRPORT_DIRECTION_CHOICES = [
        ('pickup', 'Airport Pickup'),
        ('drop', 'Airport Drop'),
    ]

    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='bookings')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    # Common fields
    ride_type = models.CharField(max_length=20, choices=RIDE_TYPES)
    pickup_location = models.CharField(max_length=255)
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Location coordinates
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)
    drop_lat = models.FloatField(null=True, blank=True)
    drop_lng = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True, help_text='Distance in kilometers')
    
    # Airport transfer specific
    flight_number = models.CharField(max_length=20, blank=True, null=True)
    airport_direction = models.CharField(max_length=10, choices=AIRPORT_DIRECTION_CHOICES, blank=True, null=True)
    
    # Rental specific
    rental_hours = models.IntegerField(blank=True, null=True)
    
    # Outstation specific
    drop_location = models.CharField(max_length=255, blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_ride_type_display()} - {self.pickup_date} {self.pickup_time}"
    
    def get_total_price(self):
        base_rates = {
            'airport': {'sedan': 800, 'suv': 1000, 'luxury': 1500},
            'rental': {'sedan': 300, 'suv': 400, 'luxury': 600},  # per hour
            'outstation': {'sedan': 12, 'suv': 15, 'luxury': 20}  # per km
        }
        
        if self.ride_type == 'airport':
            return base_rates['airport'][self.vehicle_type]
        elif self.ride_type == 'rental':
            hourly_rate = base_rates['rental'][self.vehicle_type]
            return hourly_rate * (self.rental_hours or 0)
        elif self.ride_type == 'outstation':
            km_rate = base_rates['outstation'][self.vehicle_type]
            return km_rate * (self.distance or 0)

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for booking {self.booking.id}"
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
