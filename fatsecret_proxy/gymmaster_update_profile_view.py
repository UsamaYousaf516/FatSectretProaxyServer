import requests
import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ GymMaster API Endpoint for profile update
GYMMASTER_PROFILE_UPDATE_URL = "https://elitefitnessclub.gymmasteronline.com/portal/api/v1/member/profile"
GYMMASTER_API_KEY = os.getenv("GYMMASTER_MEMBER_API_KEY")  # Member API Key

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def update_member_profile(request):
    """
    Proxy view to handle GymMaster member profile update (Multipart Form-Data with Profile Photo).
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
        form_data = request.POST.dict()
        form_data["api_key"] = GYMMASTER_API_KEY

        # ✅ Handle profile photo upload
        files = {}
        if "memberphoto" in request.FILES:
            profile_photo = request.FILES["memberphoto"]
            files["memberphoto"] = (
                profile_photo.name,
                profile_photo.file,
                profile_photo.content_type
            )
            logger.debug("🖼️ Updating Profile Photo: %s", profile_photo.name)

        logger.debug("📤 Forwarding profile update request to GymMaster: %s", GYMMASTER_PROFILE_UPDATE_URL)
        logger.debug("📝 Form Data: %s", form_data)

        # ✅ Send Multipart request
        response = requests.post(
            GYMMASTER_PROFILE_UPDATE_URL,
            data=form_data,
            files=files,
            timeout=15
        )

        # ✅ Log and return response
        logger.debug("📥 GymMaster Response Status: %d", response.status_code)
        logger.debug("📄 GymMaster Response Content: %s", response.text)

        return JsonResponse(response.json(), safe=False, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.exception("🚨 Request to GymMaster failed")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
