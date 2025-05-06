from django import forms
from .models import Booking, Review
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, Div

# Default airport location
PATNA_AIRPORT = {
    "address": "Jay Prakash Narayan International Airport, Patna, Bihar, India",
    "airport_lat": 25.5913,
    "airport_lng": 85.0880
}

class BookingForm(forms.ModelForm):
    VEHICLE_CHOICES = [
        ('sedan', 'Sedan - ₹12/km'),
        ('suv', 'SUV - ₹15/km'),
        ('luxury', 'Luxury - ₹20/km'),
    ]

    # Hidden fields to store coordinates
    pickup_lat = forms.FloatField(widget=forms.HiddenInput(), required=False)
    pickup_lng = forms.FloatField(widget=forms.HiddenInput(), required=False)
    drop_lat = forms.FloatField(widget=forms.HiddenInput(), required=False)
    drop_lng = forms.FloatField(widget=forms.HiddenInput(), required=False)
    distance = forms.FloatField(widget=forms.HiddenInput(), required=False)

    # Common fields
    pickup_location = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Enter pickup location'}))
    pickup_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    pickup_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    vehicle_type = forms.ChoiceField(choices=VEHICLE_CHOICES)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requirements?'}))

    # Airport transfer specific
    airport_direction = forms.ChoiceField(
        choices=Booking.AIRPORT_DIRECTION_CHOICES,
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'btn-check'}),
        initial='pickup'
    )
    flight_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter flight number'}))
    drop_location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter drop location'})
    )

    # Rental specific
    rental_hours = forms.IntegerField(
        required=False,
        min_value=2,
        max_value=12,
        widget=forms.NumberInput(attrs={'placeholder': 'Number of hours (minimum 2)'}),
        help_text='Minimum 2 hours, maximum 12 hours'
    )

    # Outstation specific
    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Booking
        fields = [
            'ride_type', 'pickup_location', 'pickup_date', 'pickup_time',
            'vehicle_type', 'notes', 'airport_direction', 'flight_number',
            'drop_location', 'rental_hours', 'return_date', 'pickup_lat',
            'pickup_lng', 'drop_lat', 'drop_lng', 'distance'
        ]

    def __init__(self, *args, **kwargs):
        ride_type = kwargs.pop('ride_type', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        # Common layout elements
        common_fields = [
            'ride_type',  # Hidden field for ride type
            Row(
                Column('pickup_location', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            # Hidden coordinate fields
            Field('pickup_lat', type="hidden"),
            Field('pickup_lng', type="hidden"),
            Field('drop_lat', type="hidden"),
            Field('drop_lng', type="hidden"),
            Field('distance', type="hidden"),
            Row(
                Column('pickup_date', css_class='form-group col-md-6 mb-0'),
                Column('pickup_time', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('vehicle_type', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
        ]

        # Add ride type specific fields
        if ride_type == 'airport':
            common_fields.extend([
                Row(
                    Column(
                        Div(
                            'airport_direction',
                            css_class='btn-group w-100 mb-3',
                            role='group',
                            **{'aria-label': 'Airport direction'}
                        ),
                        css_class='form-group col-md-12 mb-0'
                    ),
                    css_class='form-row'
                ),
                Row(
                    Column('flight_number', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('drop_location', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
            ])

            # Set initial airport direction and location
            self.fields['airport_direction'].initial = 'pickup'
            direction = self.initial.get('airport_direction', 'pickup')
            
            if direction == 'pickup':
                self.fields['drop_location'].initial = PATNA_AIRPORT['address']
                self.initial['drop_lat'] = PATNA_AIRPORT['airport_lat']
                self.initial['drop_lng'] = PATNA_AIRPORT['airport_lng']
            else:
                self.fields['pickup_location'].initial = PATNA_AIRPORT['address']
                self.initial['pickup_lat'] = PATNA_AIRPORT['airport_lat']
                self.initial['pickup_lng'] = PATNA_AIRPORT['airport_lng']

        elif ride_type == 'rental':
            common_fields.extend([
                Row(
                    Column('rental_hours', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
            ])
        elif ride_type == 'outstation':
            common_fields.extend([
                Row(
                    Column('drop_location', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('return_date', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
            ])

        # Add notes field and submit button
        common_fields.extend([
            Row(
                Column('notes', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Book Now', css_class='btn btn-primary')
        ])

        self.helper.layout = Layout(*common_fields)

        # Set initial ride type and hide irrelevant fields
        if ride_type:
            self.fields['ride_type'].initial = ride_type
            self.fields['ride_type'].widget = forms.HiddenInput()

            if ride_type != 'airport':
                self.fields['flight_number'].widget = forms.HiddenInput()
                self.fields['airport_direction'].widget = forms.HiddenInput()
            if ride_type != 'rental':
                self.fields['rental_hours'].widget = forms.HiddenInput()
            if ride_type not in ['airport', 'outstation']:
                self.fields['drop_location'].widget = forms.HiddenInput()
            if ride_type != 'outstation':
                self.fields['return_date'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        ride_type = cleaned_data.get('ride_type')
        
        # Validate coordinates are present
        if not cleaned_data.get('pickup_lat') or not cleaned_data.get('pickup_lng'):
            raise forms.ValidationError('Please select a valid pickup location on the map')
            
        if ride_type in ['airport', 'outstation']:
            if not cleaned_data.get('drop_lat') or not cleaned_data.get('drop_lng'):
                raise forms.ValidationError('Please select a valid drop location on the map')
        
        if ride_type == 'airport':
            if not cleaned_data.get('flight_number'):
                raise forms.ValidationError('Flight number is required for airport transfers')
            if not cleaned_data.get('airport_direction'):
                raise forms.ValidationError('Please select airport pickup or drop')
            if not cleaned_data.get('drop_location'):
                raise forms.ValidationError('Drop location is required for airport transfers')
            
            # Validate airport location based on direction
            direction = cleaned_data.get('airport_direction')
            if direction == 'pickup':
                if (cleaned_data.get('drop_lat') != PATNA_AIRPORT['airport_lat'] or 
                    cleaned_data.get('drop_lng') != PATNA_AIRPORT['airport_lng']):
                    raise forms.ValidationError('Drop location must be Patna Airport for airport pickup')
            else:  # direction == 'drop'
                if (cleaned_data.get('pickup_lat') != PATNA_AIRPORT['airport_lat'] or 
                    cleaned_data.get('pickup_lng') != PATNA_AIRPORT['airport_lng']):
                    raise forms.ValidationError('Pickup location must be Patna Airport for airport drop')
        
        elif ride_type == 'rental':
            rental_hours = cleaned_data.get('rental_hours')
            if not rental_hours:
                raise forms.ValidationError('Number of hours is required for rentals')
            if rental_hours < 2:
                raise forms.ValidationError('Minimum rental duration is 2 hours')
            if rental_hours > 12:
                raise forms.ValidationError('Maximum rental duration is 12 hours')
        
        elif ride_type == 'outstation':
            if not cleaned_data.get('drop_location'):
                raise forms.ValidationError('Drop location is required for outstation trips')
            if not cleaned_data.get('return_date'):
                raise forms.ValidationError('Return date is required for outstation trips')
            
            # Validate return date is after pickup date
            pickup_date = cleaned_data.get('pickup_date')
            return_date = cleaned_data.get('return_date')
            if pickup_date and return_date and return_date < pickup_date:
                raise forms.ValidationError('Return date must be after pickup date')
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        } 