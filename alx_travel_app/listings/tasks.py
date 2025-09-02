from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Booking

@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id):
    """
    Send booking confirmation email asynchronously
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        user = booking.user
        listing = booking.listing
        
        subject = f'Booking Confirmation - {listing.title}'
        
        # HTML email content
        html_message = render_to_string('listings/email/booking_confirmation.html', {
            'user': user,
            'booking': booking,
            'listing': listing,
        })
        
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f"Email sent successfully to {user.email}"
        
    except Booking.DoesNotExist:
        self.retry(countdown=60 * 5, max_retries=3)  # Retry after 5 minutes
    except Exception as e:
        self.retry(exc=e, countdown=60 * 5, max_retries=3)
