ALX Travel App with Celery Background Tasks

A Django-based travel booking application with asynchronous email notifications using Celery and RabbitMQ.
Features

    Property Listings Management: Create, read, update, and delete travel property listings

    Booking System: Users can book available properties

    Asynchronous Email Notifications: Automatic booking confirmation emails sent via Celery background tasks

    Real-time Task Monitoring: Monitor Celery tasks using Flower dashboard

    RESTful API: Full REST API built with Django REST Framework

Technology Stack

    Backend: Django 4.x, Django REST Framework

    Task Queue: Celery with Redis as message broker and result backend

    Email: Django SMTP email backend

    Database: SQLite (default, can be configured for PostgreSQL/MySQL)

    Monitoring: Flower for Celery task monitoring

Project Structure
text

alx_travel_app_0x03/
├── listings/
│   ├── migrations/
│   ├── templates/
│   │   └── listings/
│   │       └── email/
│   │           └── booking_confirmation.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py          # Celery tasks
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── alx_travel_app_0x03/
│   ├── __init__.py
│   ├── celery.py         # Celery configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
└── README.md

Installation & Setup
Prerequisites

    Python 3.8+

    Redis server

    SMTP email account (Gmail, SendGrid, etc.)

1. Clone and Setup Project
bash

# Clone the project (if not already done)
git clone <repository-url>
cd alx_travel_app_0x03

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

2. Configure Environment Variables

Update alx_travel_app_0x03/settings.py with your configuration:
python

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Celery Configuration (if using Redis)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

3. Database Setup
bash

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

4. Start Services

Open multiple terminal windows:

Terminal 1 - Start Redis:
bash

redis-server

Terminal 2 - Start Django Development Server:
bash

python manage.py runserver

Terminal 3 - Start Celery Worker:
bash

celery -A alx_travel_app_0x03 worker --loglevel=info

Terminal 4 - Start Flower Monitoring (Optional):
bash

celery -A alx_travel_app_0x03 flower

API Endpoints

    GET /api/listings/ - List all properties

    POST /api/listings/ - Create new property listing

    GET /api/listings/{id}/ - Get specific property details

    PUT /api/listings/{id}/ - Update property

    DELETE /api/listings/{id}/ - Delete property

    GET /api/bookings/ - List all bookings

    POST /api/bookings/ - Create new booking (triggers email)

Testing the Email Feature
Method 1: Using the API

    Create a booking via POST request to /api/bookings/

    Check Celery worker logs to see email task execution

    Verify email delivery in the recipient's inbox

Method 2: Direct Task Testing

Create a test script test_email.py:
python

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app_0x03.settings')
django.setup()

from listings.tasks import send_booking_confirmation_email

# Test the email task
result = send_booking_confirmation_email.delay(
    booking_id=999,
    user_email='test@example.com',
    listing_title='Test Beach Villa',
    check_in_date='2024-01-15',
    check_out_date='2024-01-20'
)

print(f"Task ID: {result.id}")
print("Email task triggered successfully!")

Run the test:
bash

python test_email.py

Monitoring Tasks

Access the Flower dashboard at http://localhost:5555 to:

    View active tasks

    Monitor task history

    Check worker status

    Inspect task results and failures

Customization
Modifying Email Templates

Edit listings/templates/listings/email/booking_confirmation.html to customize the email design and content.
Adding New Background Tasks

    Create new functions in listings/tasks.py decorated with @shared_task

    Call them using .delay() method from your views

    Restart Celery worker to pick up new tasks

Configuring Different Email Providers

Update SMTP settings in settings.py:
python

# For SendGrid
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'

# For Amazon SES
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_ACCESS_KEY_ID = 'your-access-key'
AWS_SES_SECRET_ACCESS_KEY = 'your-secret-key'

Troubleshooting
Common Issues

    Celery worker not starting: Ensure Redis is running

    Emails not sending: Check SMTP configuration and credentials

    Tasks not executing: Verify Celery worker is running and connected to Redis

    Module errors: Ensure all dependencies are installed from requirements.txt

Debugging Tips

    Check Celery worker logs for task execution details

    Use Flower dashboard to monitor task queue

    Test email configuration with Django shell:
    python

    from django.core.mail import send_mail
    send_mail('Test Subject', 'Test message', 'from@example.com', ['to@example.com'])

Contributing

    Fork the repository

    Create a feature branch

    Make your changes

    Add tests for new functionality

    Submit a pull request

License

This project is part of the ALX Software Engineering program.
