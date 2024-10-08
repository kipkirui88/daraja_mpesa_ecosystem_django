from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
import requests
import base64
import datetime
import os
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.conf import settings


def normalize_phone_number(phone_number):
    # Remove any spaces or dashes from the phone number
    phone_number = phone_number.replace(" ", "").replace("-", "")

    if phone_number.startswith("0"):
        # Replace leading 0 with 254
        phone_number = "254" + phone_number[1:]
    elif not phone_number.startswith("254"):
        # If the phone number doesn't start with 254, prepend it
        phone_number = "254" + phone_number

    return phone_number

from drf_spectacular.utils import extend_schema
class PaymentViewSet(viewsets.ViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @extend_schema(
        summary="Initiate M-Pesa Payment",
        description="Initiates an M-Pesa payment by calling the Safaricom API",
        responses={200: PaymentSerializer}
    )
    def create(self, request):
        phone_number = request.data.get('phone_number')
        amount = request.data.get('amount')

        response = self.perform_stk_push(phone_number, amount)
        data = response.json()

        payment = Payment(phone_number=phone_number, amount=amount)
        payment.save()

        return Response(data)

    def perform_stk_push(self, phone_number, amount):
        # Your M-Pesa API consumer key and secret
        consumer_key = '9uvkU2GwA7E5ygZrfHrAbXX9A1Af8w5bXUO8o1IOeaVo55h9'
        consumer_secret = 'd1DPs2ZjFjDrcMY1Fqh26xeWPQzHRVZXcaWrGkA9fJJGYeE7LP5s2tjtDGDWwgZX'

        credentials = base64.b64encode((consumer_key + ':' + consumer_secret).encode()).decode()
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        headers = {'Authorization': 'Basic ' + credentials, 'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers)
        access_token = response.json()['access_token']

        business_short_code = '174379'
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        transaction_type = 'CustomerPayBillOnline'
        account_reference = 'Hezekiah'
        callback_url = 'https://daraja-mpesa-ecosystem-django.onrender.com/api/mpesa/callback/'
        transaction_desc = 'Test Payment'
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

        payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': transaction_type,
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': business_short_code,
            'PhoneNumber': phone_number,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }

        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        return response


@api_view(['POST'])
def mpesa_callback(request):
    print(f"Callback Data: {request.data}")
    callback_data = request.data
    
    # Log the callback data
    log_callback_data(callback_data)
    
    # Extract necessary details
    result_code = callback_data['Body']['stkCallback']['ResultCode']
    result_description = callback_data['Body']['stkCallback']['ResultDesc']
    merchant_request_id = callback_data['Body']['stkCallback']['MerchantRequestID']
    checkout_request_id = callback_data['Body']['stkCallback']['CheckoutRequestID']
    
    # Check if the transaction was successful (ResultCode 0 means success)
    if result_code == 0:
        print("Successful payment")
        amount = callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        phone_number = callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']
        
        # Find and update the payment record
        payment = Payment.objects.filter(phone_number=phone_number, amount=amount).first()
        if payment:
            payment.result_code = result_code
            payment.result_description = result_description
            payment.status = 'Completed'
            payment.save()
        
        return JsonResponse({'status': 'Success', 'message': 'Payment processed successfully'})
    
    else:
        # For failed transactions, update with result_code and result_description
        print("Payment failed or cancelled")
        # You might want to search by CheckoutRequestID or another identifier
        payment = Payment.objects.filter(phone_number=callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']).first()
        if payment:
            payment.result_code = result_code
            payment.result_description = result_description
            payment.status = 'Failed'  # Mark as failed
            payment.save()
        
        return JsonResponse({'status': 'Failed', 'message': result_description})

# import subprocess
def log_callback_data(callback_data):
    log_file_path = os.path.join(settings.BASE_DIR, 'mpesa_callback_logs.txt')
    try:
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"Callback Data: {callback_data}\n")
        print(f"Callback data successfully logged to {log_file_path}")
    except Exception as e:
        print(f"Failed to write log: {e}")