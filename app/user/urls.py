"""url mapping for api  view"""

from django.urls import path
from user.views import UserAPIView, UserAuthTokenView, ManagerUserApiView

app_name = 'user'

urlpatterns = [
    path('create/', UserAPIView.as_view(), name='create'),
    path('token/', UserAuthTokenView.as_view(), name='token'),
    path('me/', ManagerUserApiView.as_view(), name='me'),
]