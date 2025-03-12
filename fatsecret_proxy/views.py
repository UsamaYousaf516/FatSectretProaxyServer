import requests
import os
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FATSECRET_BASE_URL = "https://platform.fatsecret.com/rest/"  # ✅ New base URL

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def fatsecret_proxy(request, method_path):
    """
    Proxy function to forward API requests to FatSecret, handling GET and POST.
    Uses the new URL-based API format instead of 'method' parameter.
    """

    # ✅ Extract Authorization header (access token)
    access_token = request.headers.get("Authorization")

    if not access_token:
        logger.error("🚨 Missing Authorization header")
        return JsonResponse({"error": "Missing Authorization header"}, status=401)

    # ✅ Construct the full URL (new FatSecret API format)
    fatsecret_url = f"{FATSECRET_BASE_URL}{method_path}"  # Example: https://platform.fatsecret.com/rest/food-sub-categories/v2
    logger.debug(f"📤 Sending request to FatSecret: {request.method} {fatsecret_url}")

    # ✅ Prepare headers
    headers = {
        "Authorization": access_token,  # Pass token to FatSecret
        "Content-Type": "application/json",
    }

    # ✅ Convert query parameters
    params = request.GET.dict()
    params["format"] = "json"  # Ensure JSON response

    # ✅ Handle GET Requests
    try:
        if request.method == "GET":
            response = requests.get(fatsecret_url, params=params, headers=headers)

        # ✅ Handle POST Requests
        elif request.method == "POST":
            try:
                body_data = json.loads(request.body.decode("utf-8"))  # Parse JSON body
            except json.JSONDecodeError:
                logger.error("🚨 Invalid JSON data received in request")
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            logger.debug(f"📦 Request Body: {body_data}")  # Log request body
            response = requests.post(fatsecret_url, json=body_data, headers=headers,timeout=20,allow_redirects=False  # ✅ Prevents unexpected redirects)

        else:
            return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)

        # ✅ Log the FatSecret response
        logger.debug(f"📥 FatSecret Response Status Code: {response.status_code}")
        logger.debug(f"📄 FatSecret Response Content: {response.text}")

        # ✅ Ensure the response contains valid JSON
        if response.status_code != 200:
            logger.error(f"🚨 FatSecret API Error: {response.status_code}")
            return JsonResponse({
                "error": "FatSecret API Error",
                "status_code": response.status_code,
                "response": response.text,
               
            }, status=response.status_code)

        return JsonResponse(response.json(), safe=False)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to FatSecret failed")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
