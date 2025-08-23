from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.exceptions import ValidationError
import requests
import json
from .models import Booking, Payment
from .serializers import PaymentSerializer
from .tasks import send_payment_confirmation_email

class ChapaAPI:
    def __init__(self):
        self.secret_key = settings.CHAPA_SECRET_KEY
        self.base_url = settings.CHAPA_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initialize_payment(self, email, amount, currency, tx_ref, first_name=None, last_name=None, phone_number=None, callback_url=None, return_url=None):
        """
        Initialize payment with Chapa API
        """
        url = f"{self.base_url}/transaction/initialize"
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name or "",
            "last_name": last_name or "",
            "phone_number": phone_number or "",
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": return_url,
            "customization": {
                "title": "ALX Travel App",
                "description": "Booking Payment"
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Chapa API error: {str(e)}")
    
    def verify_payment(self, transaction_id):
        """
        Verify payment status with Chapa API
        """
        url = f"{self.base_url}/transaction/verify/{transaction_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Chapa verification error: {str(e)}")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request, booking_id):
    """
    Initiate payment for a booking
    POST /api/bookings/<booking_id>/payments/initiate/
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if payment already exists
    if hasattr(booking, 'payment'):
        return Response(
            {'error': 'Payment already initiated for this booking'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    chapa_api = ChapaAPI()
    tx_ref = f"alx_travel_{booking.id}_{uuid.uuid4().hex[:8]}"
    
    try:
        # Initialize payment with Chapa
        payment_data = chapa_api.initialize_payment(
            email=request.user.email,
            amount=float(booking.total_price),
            currency='ETB',
            tx_ref=tx_ref,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            callback_url=f"{settings.BASE_URL}/api/payments/verify/",
            return_url=f"{settings.FRONTEND_URL}/booking/{booking.id}/payment-complete/"
        )
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            transaction_id=tx_ref,
            chapa_reference=payment_data.get('data', {}).get('reference'),
            status='pending'
        )
        
        return Response({
            'payment_url': payment_data.get('data', {}).get('checkout_url'),
            'transaction_id': tx_ref,
            'message': 'Payment initiated successfully'
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def verify_payment(request):
    """
    Verify payment status (webhook from Chapa)
    POST /api/payments/verify/
    """
    transaction_id = request.data.get('tx_ref')
    chapa_reference = request.data.get('chapa_reference')
    
    if not transaction_id:
        return Response(
            {'error': 'Transaction reference required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    payment = get_object_or_404(Payment, transaction_id=transaction_id)
    chapa_api = ChapaAPI()
    
    try:
        verification_data = chapa_api.verify_payment(chapa_reference)
        
        if verification_data.get('status') == 'success':
            payment.status = 'completed'
            payment.chapa_reference = chapa_reference
            payment.payment_method = verification_data.get('data', {}).get('payment_method')
            payment.save()
            
            # Update booking status
            payment.booking.status = 'confirmed'
            payment.booking.save()
            
            # Send confirmation email
            send_payment_confirmation_email.delay(
                payment.booking.user.email,
                payment.booking.id,
                payment.transaction_id
            )
            
            return Response({'status': 'Payment verified successfully'})
        else:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': 'Payment verification failed'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, booking_id):
    """
    Get payment status for a booking
    GET /api/bookings/<booking_id>/payments/status/
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = get_object_or_404(Payment, booking=booking)
    
    serializer = PaymentSerializer(payment)
    return Response(serializer.data)
