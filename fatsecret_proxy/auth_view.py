import requests
import os
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FATSECRET_OAUTH_URL = "https://oauth.fatsecret.com/connect/token"
FATSECRET_CLIENT_ID = os.getenv("FATSECRET_CLIENT_ID")
FATSECRET_CLIENT_SECRET = os.getenv("FATSECRET_CLIENT_SECRET")

@csrf_exempt
def get_access_token(request):
    """
    Fetches an OAuth access token from FatSecret.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    # Prepare Basic Auth Header
    auth_string = f"{FATSECRET_CLIENT_ID}:{FATSECRET_CLIENT_SECRET}"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_encoded}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "basic",
    }

    # Make request to FatSecret OAuth server
    response = requests.post(FATSECRET_OAUTH_URL, headers=headers, data=data)

    return JsonResponse(response.json(), safe=False)
