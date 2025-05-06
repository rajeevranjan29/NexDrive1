from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Driver, Rider, Vehicle
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

class RiderRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True, help_text='This will be your username')
    phone_number = forms.CharField(max_length=17, required=True)
    gender = forms.ChoiceField(choices=Rider.GENDER_CHOICES, required=False)
    profile_picture = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Rider.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                gender=self.cleaned_data['gender'],
                profile_picture=self.cleaned_data.get('profile_picture')
            )
        return user

class DriverRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='This will be used for login'
    )
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=17, required=True)
    license_number = forms.CharField(max_length=20, required=True)
    profile_picture = forms.ImageField(required=False)
    
    # Vehicle Information
    vehicle_make = forms.CharField(
        max_length=50,
        required=True,
        help_text='e.g., Toyota, Honda, etc.'
    )
    vehicle_model = forms.CharField(
        max_length=50,
        required=True,
        help_text='e.g., Camry, Civic, etc.'
    )
    vehicle_year = forms.IntegerField(
        required=True,
        min_value=1990,
        max_value=2024,
        help_text='Year of manufacture'
    )
    vehicle_color = forms.CharField(
        max_length=30,
        required=True
    )
    vehicle_plate_number = forms.CharField(
        max_length=20,
        required=True,
        help_text='Vehicle registration plate number'
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text='Your password must contain at least 8 characters.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        help_text='Enter the same password as before, for verification.'
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name',
            'phone_number', 'license_number', 'vehicle_make',
            'vehicle_model', 'vehicle_year', 'vehicle_color',
            'vehicle_plate_number', 'password1', 'password2'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        if not commit:
            return super().save(commit=False)
            
        try:
            with transaction.atomic():
                # Create the user first
                user = super().save(commit=False)
                user.username = self.cleaned_data['email']
                user.email = self.cleaned_data['email']
                user.first_name = self.cleaned_data['first_name']
                user.last_name = self.cleaned_data['last_name']
                user.save()
                
                # Create the driver instance
                driver = Driver.objects.create(
                    user=user,
                    phone_number=self.cleaned_data['phone_number'],
                    license_number=self.cleaned_data['license_number'],
                    profile_picture=self.cleaned_data.get('profile_picture')
                )
                
                # Create the vehicle instance
                Vehicle.objects.create(
                    driver=driver,
                    vehicle_number=self.cleaned_data['vehicle_plate_number'],
                    model=f"{self.cleaned_data['vehicle_make']} {self.cleaned_data['vehicle_model']} ({self.cleaned_data['vehicle_year']})",
                    vehicle_type='SEDAN',
                    capacity=4,
                    ac_available=True,
                    insurance_valid_till=timezone.now().date() + timedelta(days=365),
                    registration_valid_till=timezone.now().date() + timedelta(days=365),
                    is_active=True
                )
                
                return user
                
        except Exception as e:
            # If any error occurs, make sure to clean up
            if user.pk:
                user.delete()
            raise forms.ValidationError(f"Registration failed. Please try again. Error: {str(e)}") 