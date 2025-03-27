import requests
import json
import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from base64 import b64encode

# ✅ Load environment variables
load_dotenv()

# ✅ GymMaster GateKeeper Base URL
GM_SITE_NAME = os.getenv("GM_SITE_NAME")  # e.g., "yourgym"
GM_API_KEY = os.getenv("GM_GATEKEEPER_API_KEY")  # API Key

if not GM_SITE_NAME or not GM_API_KEY:
    raise ValueError("🚨 Missing GM_SITE_NAME or GM_GATEKEEPER_API_KEY in .env")

GM_GATEKEEPER_BASE_URL = f"https://{GM_SITE_NAME}.gymmasteronline.com/gatekeeper_api/v2/"

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def gatekeeper_proxy(request, path):
    """
    Generic proxy to forward GET and POST requests to GymMaster GateKeeper API.
    """

    # ✅ Construct the full GymMaster GateKeeper API URL
    gymmaster_url = f"{GM_GATEKEEPER_BASE_URL}{path}"

    # ✅ Prepare Basic Authentication Header
    auth_string = f"{GM_SITE_NAME}:{GM_API_KEY}"
    auth_encoded = b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_encoded}",
        "Content-Type": "application/json",
    }

    logger.debug("📤 Forwarding request to GymMaster GateKeeper: %s", gymmaster_url)
    logger.debug("🔑 Headers: %s", headers)

    try:
        if request.method == "GET":
            # ✅ Forward GET request (pass query parameters)
            response = requests.get(gymmaster_url, headers=headers, params=request.GET)

        elif request.method == "POST":
            # ✅ Ensure request contains JSON
            try:
                request_data = json.loads(request.body)  # Parse JSON data
            except json.JSONDecodeError:
                logger.error("🚨 Invalid JSON format received")
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

            # ✅ Forward POST request (pass JSON body)
            response = requests.post(gymmaster_url, headers=headers, json=request_data)

        else:
            return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)

        # ✅ Log Response
        logger.debug("📥 GymMaster Response Status: %d", response.status_code)
        logger.debug("📄 GymMaster Response Content: %s", response.text)

        # ✅ Return GymMaster's JSON Response
        return JsonResponse(response.json(), safe=False, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to GymMaster GateKeeper failed")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
