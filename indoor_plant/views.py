import hmac
import hashlib
import subprocess
import logging
from dotenv import load_dotenv
import os

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

@csrf_exempt
def update_from_github(request):
    # Log the request headers
    logger.info(f"Received webhook request with headers: {dict(request.headers)}")
    
    # Verify GitHub webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        logger.error("No signature found in request")
        return HttpResponse('No signature', status=400)

    # Webhook secret - make sure this matches exactly what you set in GitHub
    secret = settings.GITHUB_WEBHOOK_SECRET.encode()
    
    # Calculate expected signature
    expected = 'sha256=' + hmac.new(
        secret,
        request.body,
        hashlib.sha256
    ).hexdigest()

    logger.info(f"Received signature: {signature}")
    logger.info(f"Expected signature: {expected}")

    if not hmac.compare_digest(signature, expected):
        logger.error("Invalid signature")
        return HttpResponse('Invalid signature', status=403)

    # Run update script
    try:
        result = subprocess.run(['/home/nevus/update_from_github.sh'], shell=True, capture_output=True, text=True)
        logger.info(f"Update script output: {result.stdout}")
        if result.stderr:
            logger.error(f"Update script errors: {result.stderr}")
        return HttpResponse('Updated successfully')
    except Exception as e:
        logger.error(f"Error running update script: {str(e)}")
        return HttpResponse(f'Error updating: {str(e)}', status=500) 

@csrf_exempt  # or use {% csrf_token %} in form instead
def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            message = Mail(
                from_email='nebullii@icloud.com',
                to_emails=email,
                subject='Welcome to Indoor Plant Store!',
                plain_text_content='Thanks for subscribing! Stay tuned for plant care tips and offers.')

            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                sg.send(message)
                messages.success(request, "Thanks for subscribing!")
            except Exception as e:
                print(e)
                messages.error(request, "Oops! Subscription failed. Try again.")
        return redirect("/")

def home(request):
    featured_products = Product.objects.filter(featured=True)
    hot_selling_products = Product.objects.filter(hot_selling=True)
    return render(request, 'products/featured_products.html', {
        'featured_products': featured_products,
        'hot_selling_products': hot_selling_products,
    })