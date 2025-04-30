import requests
import json
import os
import africastalking
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings
from dotenv import load_dotenv
import logging
import threading
import time
from functools import lru_cache

# Set up logging with less verbose output for production
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Load environment variables once at startup
load_dotenv()

# API configuration with sane defaults
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000/api/')

# Africa's Talking configuration
username = os.environ.get('AT_USERNAME', 'sandbox')
api_key = os.environ.get('AT_API_KEY')

# Initialize Africa's Talking SDK once at startup
if api_key:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
else:
    logger.warning("Africa's Talking API key is missing! SMS functionality will not work.")
    sms = None

# Cache configuration
CACHE_TIMEOUT = 3600  # 1 hour cache for static data

# Preload and cache static data
COUNTIES = {
    '1': 'Nairobi',
    '2': 'Mombasa',
    '3': 'Kisumu',
    '4': 'Kakamega',
    '5': 'Busia'
}

INTERESTS_MAP = {
    '1': 'Coding',
    '2': 'Graphics',
    '3': 'Animation',
    '4': 'Design'
}

RESOURCE_CACHE_KEY = 'resource_data'
# Preload resources into cache
RESOURCES = {
    'Coding': [
        "HTML Basics - structure first",
        "CSS - make it look good",
        "JavaScript - add interactivity"
    ],
    'Graphics': [
        "Color Theory - understand palettes",
        "Composition - rule of thirds",
        "Typography basics"
    ],
    'Animation': [
        "12 Principles of Animation",
        "Frame by frame technique",
        "Tweening basics"
    ],
    'Design': [
        "User experience fundamentals",
        "Interface design principles",
        "Prototyping methods"
    ]
}

def send_sms_async(recipients, message):
    """
    Send SMS asynchronously in a background thread
    
    Args:
        recipients (str or list): Phone number(s) in international format
        message (str): The message to send
    """
    def _send(recips, msg):
        try:
            if sms is None:
                logger.error("Cannot send SMS - Africa's Talking API not initialized")
                return

            # Format recipients
            if isinstance(recips, str):
                recips = [recips]
                
            formatted_recipients = [
                f"+{phone}" if not phone.startswith('+') else phone 
                for phone in recips
            ]
            
            # Send the message
            response = sms.send(
                message=msg, 
                recipients=formatted_recipients,
                sender_id="10136"
            )
            
            if response and "SMSMessageData" in response and "Recipients" in response["SMSMessageData"]:
                successful = any(recipient["status"] == "Success" for recipient in response["SMSMessageData"]["Recipients"])
                logger.info(f"SMS sent successfully: {successful}")
            else:
                logger.warning(f"SMS sending failed with response: {response}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
    
    # Start the SMS sending in a background thread, passing the parameters
    threading.Thread(target=_send, args=(recipients, message)).start()

def send_welcome_sms(phone_number, name, interests):
    """
    Send a welcome SMS with resources to the user after registration
    """
    interests_str = ', '.join(interests)
    message = f"Hello {name}, thank you for registering on our Mentorship Platform! "
    message += f"Based on your interests in {interests_str}, "
    message += "we've matched you with a mentor who will contact you soon. "
    message += "Meanwhile, check out these resources:\n"
    
    # Only add up to 3 resources to keep SMS short
    resource_count = 0
    for interest in interests[:3]:
        if interest in RESOURCES and resource_count < 3:
            message += f"- {interest}: https://bit.ly/{interest.lower()}-basics\n"
            resource_count += 1
    
    message += "We're excited to have you on board!"
    
    # Send SMS asynchronously
    send_sms_async(phone_number, message)
    return True

@lru_cache(maxsize=128)
def get_resources_for_category(category):
    """
    Get cached resources for a category
    """
    if category in RESOURCES:
        return RESOURCES[category]
    return ["No resources available"]

def make_api_request_async(endpoint, method='GET', data=None, callback=None):
    """
    Make an API request asynchronously
    
    Args:
        endpoint (str): The API endpoint to call
        method (str): HTTP method (GET, POST, etc.)
        data (dict): Data to send in the request
        callback (callable): Function to call with the result
    """
    def _make_request():
        url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                if callback:
                    callback(False, f"Unsupported method: {method}")
                return
                
            # Try to get JSON response, fall back to text if not JSON
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
                
            # Check if the request was successful
            if 200 <= response.status_code < 300:
                if callback:
                    callback(True, response_data)
            else:
                if callback:
                    callback(False, f"API Error: {response.status_code}")
                    
        except Exception as e:
            if callback:
                callback(False, f"Request failed: {str(e)}")
    
    # Start the API request in a background thread
    threading.Thread(target=_make_request).start()

def store_data_locally(data):
    """
    Store user data locally as a fallback
    """
    try:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"pending_registrations_{timestamp}.json"
        
        with open(file_path, 'w') as f:
            json.dump(data, f)
            
        logger.info(f"Saved registration data locally to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save data locally: {e}")
        return False

@csrf_exempt
def ussd_callback(request):
    """
    Handle USSD requests from Africa's Talking with optimized performance
    """
    if request.method != 'POST':
        return HttpResponse("Method not allowed")
    
    # Extract USSD parameters quickly
    session_id = request.POST.get('sessionId', '')
    phone_number = request.POST.get('phoneNumber', '')
    text = request.POST.get('text', '')
    
    # Only log minimal information
    logger.info(f"USSD: {session_id[:8]}..., Text: '{text}'")
    
    # Initial menu - most common case
    if text == '':
        response = "CON Welcome to the Mentorship Platform\n"
        response += "1. Register\n2. Set language (EN/SW)\n3. View tech pathways\n4. Access resources"
        return HttpResponse(response)
    
    # Handle menu based on first option for faster routing
    first_option = text.split('*')[0] if '*' in text else text
    
    # Registration flow
    if first_option == '1':
        parts = text.split('*')
        parts_count = len(parts)
        
        if parts_count == 1:
            return HttpResponse("CON Please enter your name")
        elif parts_count == 2:
            return HttpResponse("CON Enter your age")
        elif parts_count == 3:
            return HttpResponse("CON Select your county\n1. Nairobi\n2. Mombasa\n3. Kisumu\n4. Kakamega\n5. Busia")
        elif parts_count == 4:
            return HttpResponse("CON Select your interests (separated by commas)\n1. Coding\n2. Graphics\n3. Animation\n4. Design")
        elif parts_count == 5:
            # Handle registration completion
            try:
                name = parts[1].strip()
                
                # Parse age with error handling
                try:
                    age_int = int(parts[2])
                except ValueError:
                    age_int = 0
                
                county_choice = parts[3]
                interests_choices = parts[4].split(',')
                
                # Map interests choices to actual interests - faster with direct indexing
                interests = [INTERESTS_MAP.get(choice.strip(), 'Unknown') for choice in interests_choices]
                county = COUNTIES.get(county_choice, 'Unknown')

                # Create the profile data
                profile_data = {
                    'name': name,
                    'age': age_int,
                    'county': county,
                    'language': 'en',
                    'device': 'phone',
                    'interests': interests,
                    'phone_number': phone_number,
                    'communication_preference': 'ussd'
                }
                
                # Start API request asynchronously with authentication, but return response immediately
                headers = {
                    'Authorization': f'Bearer {os.environ.get("API_TOKEN", "")}',
                    'Content-Type': 'application/json'
                }
                
                # Define API callback function
                def api_callback(success, result):
                    if success:
                        logger.info("Profile created successfully")
                    else:
                        logger.error(f"API error: {result}")
                        # Store locally as backup on API failure
                        store_data_locally(profile_data)
                
                # Update make_api_request_async call to include auth headers
                def _make_api_auth_request():
                    try:
                        url = f"{API_BASE_URL.rstrip('/')}/mentee/setup/"
                        response = requests.post(
                            url, 
                            json=profile_data, 
                            headers=headers, 
                            timeout=10
                        )
                        logger.info(f"API status: {response.status_code}")
                    except Exception as e:
                        logger.error(f"API request failed: {e}")
                        store_data_locally(profile_data)
                
                # Start API request in background
                threading.Thread(target=_make_api_auth_request).start()
                
                # Send SMS in background
                send_welcome_sms(phone_number, name, interests)
                
                # Store data locally as a backup without waiting
                threading.Thread(
                    target=store_data_locally,
                    args=(profile_data,)
                ).start()
                
                # Return immediately to improve USSD response time
                return HttpResponse(
                    "END Thank you for registering! We've matched you with a mentor who will contact you soon. "
                    "Check your SMS for resources and more information."
                )
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                return HttpResponse("END Error during registration. Please try again later.")
    
    # Language setting flow - simplest flow
    elif first_option == '2':
        if text == '2':
            return HttpResponse("CON Select language\n1. English\n2. Swahili")
        elif text == '2*1':
            return HttpResponse("END Language set to English")
        elif text == '2*2':
            return HttpResponse("END Lugha imewekwa kwa Kiswahili")
    
    # Tech pathways flow - use cached data
    elif first_option == '3':
        if text == '3':
            return HttpResponse("CON Select your tech pathway\n1. Coding\n2. Graphics\n3. Animation\n4. Design")
        else:
            parts = text.split('*')
            if len(parts) == 2:
                pathway_choice = parts[1]
                pathway = INTERESTS_MAP.get(pathway_choice, 'Unknown')
                
                # Get cached resources
                resources = get_resources_for_category(pathway)
                
                response = f"END {pathway} Resources:\n"
                for i, resource in enumerate(resources, 1):
                    if i <= 3:  # Limit to 3 resources for faster response
                        response += f"{i}. {resource}\n"
                
                return HttpResponse(response)
    
    # Resources flow - use cached data
    elif first_option == '4':
        if text == '4':
            return HttpResponse("CON Select category\n1. Coding\n2. Graphics\n3. Animation\n4. Design")
        else:
            parts = text.split('*')
            if len(parts) == 2:
                category_choice = parts[1]
                category = INTERESTS_MAP.get(category_choice, 'Unknown')
                
                # Get cached resources
                resources = get_resources_for_category(category)
                
                response = f"END {category} Resources:\n"
                for i, resource in enumerate(resources, 1):
                    if i <= 3:  # Limit to 3 resources for faster response
                        response += f"{i}. {resource}\n"
                
                return HttpResponse(response)
    
    # Default fallback
    return HttpResponse("END Invalid option")