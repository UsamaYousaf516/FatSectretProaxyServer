import requests
import os
import base64
import logging  # ✅ Import logging module
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

FATSECRET_OAUTH_URL = "https://oauth.fatsecret.com/connect/token"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def get_access_token(request):
    """
    Fetches an OAuth access token from FatSecret and logs request details.
    """
    if request.method != "POST":
        logger.warning("🚨 Invalid request method: %s", request.method)
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    # ✅ Log client ID & Secret presence (without printing actual values)
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("🚨 Missing FATSECRET_CLIENT_ID or FATSECRET_CLIENT_SECRET")
        return JsonResponse({"error": "Server misconfiguration: Missing credentials"}, status=500)

    # ✅ Create Basic Auth Header
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_encoded}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials",
    }

    # ✅ Log Request Details
    logger.debug("📤 Sending request to FatSecret: %s", FATSECRET_OAUTH_URL)
    logger.debug("📝 Headers: %s", headers)
    logger.debug("📦 Payload: %s", data)

    try:
        # ✅ Make request to FatSecret OAuth server
        response = requests.post(FATSECRET_OAUTH_URL, headers=headers, data=data)

        # ✅ Log Response Status & Content
        logger.debug("📥 Response Status Code: %d", response.status_code)
        logger.debug("📄 Response Content: %s", response.text)

        # ✅ Ensure response contains valid JSON
        if response.status_code != 200:
            logger.error("🚨 FatSecret API Error: %d", response.status_code)
            return JsonResponse({
                "error": "Failed to get access token",
                "status_code": response.status_code,
                "response": response.text
            }, status=response.status_code)

        return JsonResponse(response.json(), safe=False)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to FatSecret failed")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
