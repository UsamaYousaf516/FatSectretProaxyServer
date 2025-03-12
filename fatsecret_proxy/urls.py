from django.urls import path, re_path
from .views import fatsecret_proxy
from .auth_view import get_access_token

urlpatterns = [
   path('auth/token/', get_access_token, name='get_access_token'),
   re_path(r'^(?P<method_path>[\w\-/]+)/$', fatsecret_proxy, name='fatsecret_proxy'),
   
]
