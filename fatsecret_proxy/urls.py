from django.urls import path, re_path
from .views import fatsecret_proxy
from .auth_view import get_access_token
from .gymmaster_gatekeeper_view import gatekeeper_proxy
from .gymmaster_signup_view import signup_member
from .gymmaster_login_view import login_with_email, login_with_memberid
from .gymmaster_proxy_view import gymmaster_proxy
from .gymmaster_update_profile_view import update_member_profile

urlpatterns = [
   # ✅ Authentication
   path('auth/token/', get_access_token, name='get_access_token'),

   # ✅ GymMaster API Endpoints
   path('gymmaster/signup/', signup_member, name='signup_member'),
   path('gymmaster/login/email/', login_with_email, name='login_with_email'),
   path('gymmaster/login/memberid/', login_with_memberid, name='login_with_memberid'),
   path('gymmaster/member/update/profile/', update_member_profile, name='update_member_profile'),
   re_path(r'^gymmaster/gatekeeper/(?P<path>.*)/$', gatekeeper_proxy, name='gatekeeper_proxy'), 
   re_path(r'^gymmaster/(?P<path>.*)/$', gymmaster_proxy, name='gymmaster_proxy'),
    # ✅ Dynamic API Proxy

   # ✅ FatSecret Proxy (Placed at the end to prevent conflicts)
   re_path(r'^(?P<method_path>[\w\-/]+)/$', fatsecret_proxy, name='fatsecret_proxy'),
]