import requests
from django.conf import settings
import json

FEDEX_AUTH_URL = settings.FEDEX_AUTH_URL
FEDEX_SHIPMENT_URL = settings.FEDEX_SHIPMENT_URL

def get_fedex_access_token():
    """
    Obtain OAuth2 access token from FedEx API.
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.FEDEX_API_KEY,
        "client_secret": settings.FEDEX_API_SECRET,
    }
    response = requests.post(FEDEX_AUTH_URL, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def create_fedex_shipment(shipment_type, service, declared_value, pickup_time, total_weight, length, width, height, shipping_address):
    from datetime import datetime, timedelta
    
    # Format pickup_time to FedEx expected format (YYYY-MM-DDTHH:MM:SS)
    if isinstance(pickup_time, str):
        try:
            # Parse datetime-local format and format for FedEx
            dt = datetime.fromisoformat(pickup_time.replace('Z', '').replace('T', ' '))
            pickup_time = dt.strftime('%Y-%m-%dT%H:%M:%S')
        except:
            # Fallback to tomorrow at 10 AM if parsing fails
            dt = datetime.now() + timedelta(days=1)
            pickup_time = dt.replace(hour=10, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%S')
    
    access_token = get_fedex_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    # FedEx Sandbox standard payload
    payload = {
        "accountNumber": {
            "value": settings.FEDEX_ACCOUNT_NUMBER
        },
        "requestedShipment": {
            "shipper": {
                "contact": {
                    "personName": "Shipper Name",
                    "phoneNumber": "1234567890"
                },
                "address": {
                    "streetLines": ["10 FedEx Parkway"],
                    "city": "Collierville",
                    "stateOrProvinceCode": "TN",
                    "postalCode": "38017",
                    "countryCode": "US"
                }
            },
            "recipients": [
                {
                    "contact": {
                        "personName": "Recipient Name",
                        "phoneNumber": "1234567890"
                    },
                    "address": {
                        "streetLines": ["13450 Farmcrest Ct"],
                        "city": "Herndon",
                        "stateOrProvinceCode": "VA",
                        "postalCode": "20171",
                        "countryCode": "US"
                    }
                }
            ],
            "pickupType": "USE_SCHEDULED_PICKUP",
            "serviceType": "FEDEX_GROUND",
            "packagingType": "YOUR_PACKAGING",
            "shippingChargesPayment": {
                "paymentType": "SENDER",
                "payor": {
                    "responsibleParty": {
                        "accountNumber": {
                            "value": settings.FEDEX_ACCOUNT_NUMBER
                        }
                    }
                }
            },
            "labelSpecification": {
                "imageType": "PDF",
                "labelStockType": "PAPER_4X6"
            },
            "requestedPackageLineItems": [
                {
                    "weight": {
                        "units": "LB",
                        "value": 1.0
                    },
                    "dimensions": {
                        "length": 10,
                        "width": 10,
                        "height": 3,
                        "units": "IN"
                    }
                }
            ]
        }
    }
    try:
        print(f"Sending FedEx payload: {json.dumps(payload, indent=2)}")
        response = requests.post(FEDEX_SHIPMENT_URL, headers=headers, json=payload)
        print(f"FedEx Response Status: {response.status_code}")
        print(f"FedEx Response: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Log the error details for debugging
        error_details = {
            'status_code': response.status_code,
            'response_text': response.text,
            'payload_sent': payload
        }
        print(f"FedEx API Error: {error_details}")
        raise Exception(f"FedEx API Error {response.status_code}: {response.text}") 