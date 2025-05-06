from django.urls import path
from . import views

app_name = 'driver'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('bookings/', views.bookings, name='bookings'),
    path('vehicle/', views.vehicle_info, name='vehicle'),
] 