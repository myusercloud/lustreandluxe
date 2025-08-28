import requests
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime

from decouple import config

consumer_key = config("CONSUMER_KEY")
consumer_secret = config("CONSUMER_SECRET")
lipa_na_mpesa_passkey = config("MPESA_PASSKEY")


def get_access_token():
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    json_response = response.json()
    return json_response['access_token']



def lipa_na_mpesa(phone_number, amount):
    access_token = get_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    # Credentials
    business_shortcode = "174379"  # Test Paybill for sandbox
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password = base64.b64encode((business_shortcode + lipa_na_mpesa_passkey + timestamp).encode()).decode("utf-8")

    headers = {"Authorization": "Bearer %s" % access_token}
    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,      # Customer phone number (2547XXXXXXXX)
        "PartyB": business_shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://random.ngrok.io/mpesa/callback",  # must be https
        "AccountReference": "LustreLuxe",
        "TransactionDesc": "Payment for order"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()
