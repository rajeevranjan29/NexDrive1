from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    #adress = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Rider(BaseProfile):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    #mergency_contact = models.CharField(max_length=17, blank=True)
    
    # preferred_payment_method = models.CharField(max_length=50, blank=True)
    total_rides = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Rider: {self.user.get_full_name() or self.user.username}"
    
    class Meta:
        verbose_name = 'Rider'
        verbose_name_plural = 'Riders'

class Driver(BaseProfile):
    license_number = models.CharField(max_length=20, unique=True)
    #experience_years = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    is_available = models.BooleanField(default=True)
    vehicle_capacity = models.PositiveIntegerField(default=4)
    total_trips = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    document_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Driver: {self.user.get_full_name()} - {self.license_number}"
    
    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('LUXURY', 'Luxury'),
        ('COMPACT', 'Compact'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_number = models.CharField(max_length=15, unique=True)
    model = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    capacity = models.PositiveIntegerField()
    ac_available = models.BooleanField(default=True)
    insurance_valid_till = models.DateField()
    registration_valid_till = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.model} - {self.vehicle_number}"
    
    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
