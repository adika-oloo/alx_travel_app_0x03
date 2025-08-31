from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking, Listing
from .serializers import BookingSerializer
from .tasks import send_booking_confirmation_email
from django.utils import timezone

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the booking
        booking = serializer.save()
        
        # Trigger email task asynchronously
        try:
            listing = booking.listing
            send_booking_confirmation_email.delay(
                booking_id=booking.id,
                user_email=booking.user.email,
                listing_title=listing.title,
                check_in_date=booking.check_in_date.strftime('%Y-%m-%d'),
                check_out_date=booking.check_out_date.strftime('%Y-%m-%d')
            )
        except Exception as e:
            # Log the error but don't fail the booking creation
            print(f"Failed to trigger email task: {e}")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
