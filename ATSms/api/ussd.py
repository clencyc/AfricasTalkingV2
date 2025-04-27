import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import africastalking
# Example URL of your API
API_BASE_URL = 'http://localhost:8000/api/'

load_dotenv()
username = "sandbox"
api_key = os.environ.get("AT_API_KEY")
africastalking.initialize(username, api_key)

ama = africastalking.sms


#send sms after ussd
def send_sms(request):



@csrf_exempt
def ussd_callback(request):
    """
    Handle USSD requests from Africa's Talking
    """
    if request.method == 'POST':
        session_id = request.POST.get('sessionId', None)
        service_code = request.POST.get('serviceCode', None)
        phone_number = request.POST.get('phoneNumber', None)
        text = request.POST.get('text', '')
        
        # Handle menu levels based on text
        response = ""
        
        # Initial menu
        if text == '':
            response = "CON Welcome to the Mentorship Platform\n"
            response += "1. Register\n"
            response += "2. Set language (EN/SW)\n"
            response += "3. View tech pathways\n"
            response += "4. Access resources"
            
        # Registration flow
        elif text == '1':
            response = "CON Please enter your name"
        elif text.startswith('1*') and len(text.split('*')) == 2:
            name = text.split('*')[1]
            response = "CON Enter your age"
        elif text.startswith('1*') and len(text.split('*')) == 3:
            name = text.split('*')[1]
            age = text.split('*')[2]
            response = "CON Select your county\n"
            response += "1. Nairobi\n2. Mombasa\n3. Kisumu\n4. Kakamega\n5. Busia"
        elif text.startswith('1*') and len(text.split('*')) == 4:
            name = text.split('*')[1]
            age = text.split('*')[2]
            county_choice = text.split('*')[3]
            
            # Map county choice to actual county
            counties = {
                '1': 'Nairobi',
                '2': 'Mombasa',
                '3': 'Kisumu',
                '4': 'Kakamega',
                '5': 'Busia'
            }
            county = counties.get(county_choice, 'Unknown')
            
            response = "CON Select your interests (separated by commas)\n"
            response += "1. Coding\n2. Graphics\n3. Animation\n4. Design"
        elif text.startswith('1*') and len(text.split('*')) == 5:
            name = text.split('*')[1]
            age = text.split('*')[2]
            county_choice = text.split('*')[3]
            interests_choices = text.split('*')[4].split(',')
            
            # Map interests choices to actual interests
            interests_map = {
                '1': 'Coding',
                '2': 'Graphics',
                '3': 'Animation',
                '4': 'Design'
            }
            interests = [interests_map.get(choice.strip(), 'Unknown') for choice in interests_choices]
            
            # Map county choice to actual county
            counties = {
                '1': 'Nairobi',
                '2': 'Mombasa',
                '3': 'Kisumu',
                '4': 'Kakamega',
                '5': 'Busia'
            }
            county = counties.get(county_choice, 'Unknown')
            
            # Here you would make an API call to save the mentee profile
            # This is a placeholder - in production you'd need proper auth
            profile_data = {
                'name': name,
                'age': int(age),
                'county': county,
                'device': 'phone',
                'interests': interests,
                'communication_preference': 'ussd'
            }
            
            # In a real implementation, you'd need to authenticate and send this data
            # to your API
            
            response = "END Thank you for registering! We'll match you with a mentor soon."
            
        # Language setting flow
        elif text == '2':
            response = "CON Select language\n"
            response += "1. English\n"
            response += "2. Swahili"
        elif text == '2*1':
            # Here you would make an API call to set language to English
            response = "END Language set to English"
        elif text == '2*2':
            # Here you would make an API call to set language to Swahili
            response = "END Lugha imewekwa kwa Kiswahili"
            
        # Tech pathways flow
        elif text == '3':
            response = "CON Select your tech pathway\n"
            response += "1. Coding\n"
            response += "2. Graphics\n"
            response += "3. Animation\n"
            response += "4. Design"
        elif text.startswith('3*'):
            pathway_choice = text.split('*')[1]
            
            # Map choice to actual pathway
            pathways = {
                '1': 'Coding',
                '2': 'Graphics',
                '3': 'Animation',
                '4': 'Design'
            }
            pathway = pathways.get(pathway_choice, 'Unknown')
            
            # Here you would make an API call to get pathway resources
            # In a real implementation, you'd return actual resources
            
            response = f"END {pathway} Resources:\n"
            if pathway == 'Coding':
                response += "1. Learn HTML basics: Start with structure\n"
                response += "2. CSS basics: Style your pages\n"
                response += "3. JavaScript intro: Add interactivity"
            elif pathway == 'Graphics':
                response += "1. Design principles\n"
                response += "2. Color theory basics\n"
                response += "3. Layout fundamentals"

        # Resources flow
        elif text == '4':
            response = "CON Select category\n"
            response += "1. Coding\n"
            response += "2. Graphics\n"
            response += "3. Animation\n"
            response += "4. Design"
        elif text.startswith('4*'):
            category_choice = text.split('*')[1]
            
            # Map choice to actual category
            categories = {
                '1': 'Coding',
                '2': 'Graphics',
                '3': 'Animation',
                '4': 'Design'
            }
            category = categories.get(category_choice, 'Unknown')
            
            # Here you would make an API call to get resources by category
            # In a real implementation, you'd return actual resources from your API
            
            response = f"END {category} Resources:\n"
            if category == 'Coding':
                response += "1. HTML Basics - structure first\n"
                response += "2. CSS - make it look good\n"
                response += "3. JavaScript - add interactivity"
            elif category == 'Graphics':
                response += "1. Color Theory - understand palettes\n"
                response += "2. Composition - rule of thirds\n"
                response += "3. Typography basics"
            elif category == 'Animation':
                response += "1. 12 Principles of Animation\n"
                response += "2. Frame by frame technique\n"
                response += "3. Tweening basics"
            elif category == 'Design':
                response += "1. User experience fundamentals\n"
                response += "2. Interface design principles\n"
                response += "3. Prototyping methods"
        else:
            response = "END Invalid option"
            
        return HttpResponse(response)
    else:
        return HttpResponse("Method not allowed")
