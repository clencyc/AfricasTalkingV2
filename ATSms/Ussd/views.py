from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Disable CSRF protection for this view
def ussd_api(request):
    if request.method == "POST":
        # Get parameters from the request
        session_id = request.POST.get('sessionId', '')
        service_code = request.POST.get('serviceCode', '')
        phone_number = request.POST.get('phoneNumber', '')
        text = request.POST.get('text', '')

        # Handle USSD logic
        if text == "":
            # First interaction
            response = "CON Welcome to our USSD service\n"
            response += "1. View Account\n"
            response += "2. Check Balance"
        elif text == "1":
            # User selected option 1
            response = "CON Your account details are:\n"
            response += "Name: John Doe\n"
            response += "Account Number: 123456"
        elif text == "2":
            # User selected option 2
            response = "END Your balance is KES 1,000"
        else:
            # Invalid input
            response = "END Invalid option. Please try again."

        return HttpResponse(response, content_type="text/plain")
    else:
        return HttpResponse("Invalid request method", status=405)