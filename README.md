# Nex Drive - Cab Service Provider

A web application for Nex Drive, providing cab services in Patna. This application allows users to book cabs, track rides, and manage their bookings.

## Features

- User registration and authentication
- Cab booking system
- Real-time ride tracking
- Driver management
- Booking history
- Profile management

## Setup Instructions

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

Visit http://127.0.0.1:8000/ to access the application.

## Technology Stack

- Django 5.0.1
- Bootstrap 5
- SQLite (default database)
- Django Crispy Forms "# nexdrive" 
