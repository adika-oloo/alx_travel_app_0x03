import requests
from django.http import JsonResponse
from django.conf import settings
from .models import Payment

def initiate_payment(request):
    # Example: Booking details received via POST
    booking_reference = request.POST.get("booking_reference")
    amount = request.POST.get("amount")

    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": request.POST.get("email"),
        "tx_ref": booking_reference,
        "callback_url": "http://your-domain.com/payment/verify/"
    }

    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

    response = requests.post(f"{settings.CHAPA_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("status") == "success":
        Payment.objects.create(
            booking_reference=booking_reference,
            amount=amount,
            transaction_id=data["data"]["id"],
            status="Pending"
        )
        return JsonResponse({"payment_url": data["data"]["checkout_url"]})
    return JsonResponse({"error": data.get("message")}, status=400)


def verify_payment(request):
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")

    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    response = requests.get(f"{settings.CHAPA_BASE_URL}/transaction/verify/{transaction_id}", headers=headers)
    data = response.json()

    payment = Payment.objects.get(transaction_id=transaction_id)

    if data.get("status") == "success":
        payment.status = "Completed"
    else:
        payment.status = "Failed"
    payment.save()

    # Optionally trigger Celery email task here
    return JsonResponse({"status": payment.status})
