from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_email(customer_email, booking_details):
    """
    Sends a booking confirmation email asynchronously
    """
    subject = 'Booking Confirmation'
    message = f'Thank you for your booking! Details: {booking_details}'
    recipient_list = [customer_email]

    send_mail(subject, message, None, recipient_list)
    return f'Email sent to {customer_email}'
