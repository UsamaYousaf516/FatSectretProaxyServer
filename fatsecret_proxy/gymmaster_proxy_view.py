import requests
import json
import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ GymMaster API Base URL
GYMMASTER_BASE_URL = "https://elitefitnessclub.gymmasteronline.com/portal/api/v1/"
GYMMASTER_API_KEY = os.getenv("GYMMASTER_MEMBER_API_KEY")

if not GYMMASTER_API_KEY:
    raise ValueError("🚨 Missing GYMMASTER_MEMBER_API_KEY in .env")

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def gymmaster_proxy(request, path):
    """
    Universal Proxy View for GymMaster API
    Dynamically adjusts Content-Type between JSON and FormData.
    """

    gymmaster_url = f"{GYMMASTER_BASE_URL}{path}"
    client_content_type = request.headers.get("Content-Type", "")

    logger.debug("📤 Forwarding to GymMaster: %s", gymmaster_url)
    logger.debug("💡 Client Content-Type: %s", client_content_type)

    try:
        if request.method == "GET":
            # ✅ Always append API key for GET
            params = request.GET.dict()
            params["api_key"] = GYMMASTER_API_KEY
            response = requests.get(gymmaster_url, params=params)

        elif request.method == "POST":
            headers = {}
            if "application/json" in client_content_type:
                # ✅ JSON Handling
                try:
                    body_data = json.loads(request.body)
                except json.JSONDecodeError:
                    logger.error("🚨 Invalid JSON from client.")
                    return JsonResponse({"error": "Invalid JSON format."}, status=400)

                body_data["api_key"] = GYMMASTER_API_KEY
                headers["Content-Type"] = "application/json"

                logger.debug("📝 JSON Payload: %s", body_data)

                response = requests.post(
                    gymmaster_url,
                    json=body_data,
                    headers=headers,
                    timeout=15
                )

            else:
                # ✅ Form-Data Handling
                form_data = request.POST.dict()
                form_data["api_key"] = GYMMASTER_API_KEY
                headers["Content-Type"] = "application/x-www-form-urlencoded"

                logger.debug("📝 Form Payload: %s", form_data)

                response = requests.post(
                    gymmaster_url,
                    data=form_data,
                    headers=headers,
                    timeout=15
                )

        else:
            return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)

        # ✅ Log and return GymMaster's response
        logger.debug("📥 GymMaster Response Status: %d", response.status_code)
        logger.debug("📄 GymMaster Response Content: %s", response.text)

        return JsonResponse(response.json(), safe=False, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to GymMaster failed.")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
