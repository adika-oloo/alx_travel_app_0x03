from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def send_booking_confirmation_email(booking_id, user_email, listing_title, check_in_date, check_out_date):
    """
    Send booking confirmation email asynchronously
    """
    subject = f'Booking Confirmation - {listing_title}'
    
    # HTML email content
    html_message = render_to_string('listings/email/booking_confirmation.html', {
        'listing_title': listing_title,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'booking_id': booking_id,
    })
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Email sent successfully to {user_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"





















