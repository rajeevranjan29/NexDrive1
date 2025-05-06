from django.urls import path
from . import views

app_name = 'ride'

urlpatterns = [
    # Booking URLs
    path('book/', views.create_booking, name='create_booking'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Review URLs
    path('booking/<int:booking_pk>/review/', views.create_review, name='create_review'),
    path('reviews/', views.review_list, name='review_list'),
] 