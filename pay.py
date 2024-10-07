import requests
import base64
import datetime
import json

def get_access_token():
    # Your M-Pesa API consumer key and secret
    consumer_key = '9uvkU2GwA7E5ygZrfHrAbXX9A1Af8w5bXUO8o1IOeaVo55h9'
    consumer_secret = 'd1DPs2ZjFjDrcMY1Fqh26xeWPQzHRVZXcaWrGkA9fJJGYeE7LP5s2tjtDGDWwgZX'

    # Encoding the credentials in base64 to create a basic authentication header
    credentials = base64.b64encode((consumer_key + ':' + consumer_secret).encode()).decode()

    # URL for the OAuth endpoint to generate an access token
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    # Headers for the request, including the authorization header
    headers = {
        'Authorization': 'Basic ' + credentials,
        'Content-Type': 'application/json'
    }

    # Sending a GET request to the OAuth endpoint to get an access token
    response = requests.get(url, headers=headers)

    # Parsing the response to extract the access token
    access_token = response.json()['access_token']

    # Returning the access token for use in subsequent API requests
    return access_token

def perform_stk_push(phone_number, amount):
    # Business short code for your paybill or till number
    business_short_code = '174379'

    # Your M-Pesa passkey
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

    # Current timestamp in the required format for the API (yyyyMMddHHmmss)
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # Type of transaction (e.g., Paybill)
    transaction_type = 'CustomerPayBillOnline'

    # Reference for the transaction
    account_reference = 'Hezekiah'

    # URL to receive transaction notifications
    callback_url = 'https://morning-basin-87523.herokuapp.com/callback_url.php'

    # Description of the transaction
    transaction_desc = 'Test Payment'

    # Generate the password for the transaction request by encoding business short code, passkey, and timestamp
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

    # Creating the payload with transaction details
    payload = {
        'BusinessShortCode': business_short_code,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': transaction_type,
        'Amount': amount,
        'PartyA': phone_number,  # The customer's phone number
        'PartyB': business_short_code,  # The business short code
        'PhoneNumber': phone_number,  # The customer's phone number
        'CallBackURL': callback_url,  # URL to receive transaction notifications
        'AccountReference': account_reference,  # Transaction reference
        'TransactionDesc': transaction_desc  # Transaction description
    }

    # Get an access token for authenticating the API request
    access_token = get_access_token()

    # URL for the STK push endpoint
    url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

    # Headers for the request, including the Bearer token for authorization
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    # Sending a POST request to the STK push endpoint with the payload and headers
    response = requests.post(url, json=payload, headers=headers)

    # Returning the JSON response from the API
    return response.json()

# Example usage of the function to perform an STK push
phone_number = '254727176688'  # Replace with the phone number of the customer
amount = '10'  # Replace with the amount to be charged

# Perform the STK push and print the response
response = perform_stk_push(phone_number, amount)
print(json.dumps(response, indent=4))