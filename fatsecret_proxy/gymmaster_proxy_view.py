import requests
import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ GymMaster API Base URL
GYMMASTER_BASE_URL = "https://elitefitnessclub.gymmasteronline.com/portal/api/v1/"

# ✅ GymMaster API Key
GYMMASTER_API_KEY = os.getenv("GYMMASTER_MEMBER_API_KEY")  # Ensure this is set in .env

if not GYMMASTER_API_KEY:
    raise ValueError("🚨 Missing GYMMASTER_MEMBER_API_KEY in .env")

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def gymmaster_proxy(request, path):
    """
    Universal Proxy View for GymMaster API
    - Automatically appends `api_key`
    - Supports dynamic paths (e.g., /member/profile, /member/membershiptypes)
    - Handles both GET and POST requests
    """

    # ✅ Construct full API URL
    gymmaster_url = f"{GYMMASTER_BASE_URL}{path}"
    
    # ✅ Add API key to request parameters
    params = request.GET.dict() if request.method == "GET" else {}
    params["api_key"] = GYMMASTER_API_KEY  # Always include API key

    logger.debug("📤 Forwarding request to GymMaster: %s", gymmaster_url)

    try:
        if request.method == "GET":
            # ✅ Forward GET request
            response = requests.get(gymmaster_url, params=params)

        elif request.method == "POST":
            # ✅ Forward POST request with form data
            form_data = request.POST.dict()  # Extract form data
            form_data["api_key"] = GYMMASTER_API_KEY  # ✅ Add API key

            logger.debug("📝 Payload: %s", form_data)

            response = requests.post(
                gymmaster_url,
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15
            )

        else:
            return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)

        # ✅ Log Response
        logger.debug("📥 GymMaster Response Status: %d", response.status_code)
        logger.debug("📄 GymMaster Response Content: %s", response.text)

        # ✅ Return GymMaster's JSON Response
        return JsonResponse(response.json(), safe=False, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to GymMaster failed")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
