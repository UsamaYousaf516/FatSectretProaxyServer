import requests
import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ GymMaster API Endpoint
GYMMASTER_LOGIN_URL = "https://elitefitnessclub.gymmasteronline.com/portal/api/v1/login"

# ✅ Store API Keys securely
GYMMASTER_MEMBER_API_KEY = os.getenv("GYMMASTER_MEMBER_API_KEY")  # For email/password login
GYMMASTER_STAFF_API_KEY = os.getenv("GYMMASTER_STAFF_API_KEY")  # For member ID login

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def login_with_email(request):
    """
    Proxy view to handle GymMaster login with email and password.
    """
    if request.method != "POST":
        logger.warning("🚨 Invalid request method: %s", request.method)
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    if not GYMMASTER_MEMBER_API_KEY:
        logger.error("🚨 Missing GymMaster Member API Key")
        return JsonResponse({"error": "Server misconfiguration: Missing API Key"}, status=500)

    try:
        # ✅ Extract email and password from form-data
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return JsonResponse({"error": "Email and Password are required"}, status=400)

        form_data = {
            "api_key": GYMMASTER_MEMBER_API_KEY,
            "email": email,
            "password": password,
        }

        logger.debug("📤 Forwarding email login request to GymMaster: %s", GYMMASTER_LOGIN_URL)
        logger.debug("📝 Payload: %s", form_data)

        response = requests.post(
            GYMMASTER_LOGIN_URL,
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )

        logger.debug("📥 GymMaster Response Status: %d", response.status_code)
        logger.debug("📄 GymMaster Response Content: %s", response.text)

        return JsonResponse(response.json(), safe=False, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to GymMaster failed")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)


@csrf_exempt
def login_with_memberid(request):
    """
    Proxy view to handle GymMaster login with Member ID (Staff API Key required).
    """
    if request.method != "POST":
        logger.warning("🚨 Invalid request method: %s", request.method)
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    if not GYMMASTER_STAFF_API_KEY:
        logger.error("🚨 Missing GymMaster Staff API Key")
        return JsonResponse({"error": "Server misconfiguration: Missing Staff API Key"}, status=500)

    try:
        # ✅ Extract member ID from form-data
        memberid = request.POST.get("memberid")

        if not memberid:
            return JsonResponse({"error": "Member ID is required"}, status=400)

        form_data = {
            "api_key": GYMMASTER_STAFF_API_KEY,
            "memberid": memberid,
        }

        logger.debug("📤 Forwarding member ID login request to GymMaster: %s", GYMMASTER_LOGIN_URL)
        logger.debug("📝 Payload: %s", form_data)

        response = requests.post(
            GYMMASTER_LOGIN_URL,
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )

        logger.debug("📥 GymMaster Response Status: %d", response.status_code)
        logger.debug("📄 GymMaster Response Content: %s", response.text)

        return JsonResponse(response.json(), safe=False, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to GymMaster failed")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
