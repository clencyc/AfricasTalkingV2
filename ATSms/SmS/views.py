from django.http import HttpResponse
import africastalking
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the SDK
username = "sandbox"  # Use 'sandbox' for testing in the sandbox environment
api_key = os.getenv("AT_API_KEY")
africastalking.initialize(username, api_key)

# Get the SMS service
sms = africastalking.SMS

# Define the SMS parameters
recipients = ["+254792552491"]  # List of recipient phone numbers
message = "Hello, view our startup!"
sender_id = "10136"  # Optional: Use a registered sender ID

def send_sms():
    try:
        # Send the SMS
        response = sms.send(message, recipients, sender_id)
        return response
    except Exception as e:
        return str(e)

# Define a Django view to trigger the SMS
def send_sms_view(request):
    response = send_sms()
    return HttpResponse(f"SMS Response: {response}")