import requests
import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ GymMaster API Endpoint
GYMMASTER_SIGNUP_URL = "https://elitefitnessclub.gymmasteronline.com/portal/api/v1/signup"
GYMMASTER_API_KEY = os.getenv("GYMMASTER_MEMBER_API_KEY")  # Store API key securely

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def signup_member(request):
    """
    Proxy view to handle GymMaster signup API (Multipart Form-Data with Profile Photo).
    """
    if request.method != "POST":
        logger.warning("🚨 Invalid request method: %s", request.method)
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    # ✅ Ensure API Key is present
    if not GYMMASTER_API_KEY:
        logger.error("🚨 Missing GymMaster API Key")
        return JsonResponse({"error": "Server misconfiguration: Missing API Key"}, status=500)

    try:
        # ✅ Extract form data
        form_data = request.POST.dict()  # Extract form fields
        form_data["api_key"] = GYMMASTER_API_KEY  # ✅ Add API Key

        # ✅ Handle profile photo upload
        files = {}
        if "memberphoto" in request.FILES:
            profile_photo = request.FILES["memberphoto"]
            files["memberphoto"] = (profile_photo.name, profile_photo.file, profile_photo.content_type)
            logger.debug("🖼️ Profile Photo: %s", profile_photo.name)

        logger.debug("📤 Forwarding signup request to GymMaster: %s", GYMMASTER_SIGNUP_URL)
        logger.debug("📝 Form Data: %s", form_data)

        # ✅ Send Multipart request to GymMaster
        response = requests.post(
            GYMMASTER_SIGNUP_URL,
            data=form_data,  # Sending form fields
            files=files,  # Sending file(s)
            timeout=15
        )

        # ✅ Log GymMaster's response
        logger.debug("📥 GymMaster Response Status: %d", response.status_code)
        logger.debug("📄 GymMaster Response Content: %s", response.text)

        # ✅ Return GymMaster's response to the mobile app
        return JsonResponse(response.json(), safe=False, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to GymMaster failed")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
