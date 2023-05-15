"""Create api views for users"""

from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer, UserTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

class UserAPIView(generics.CreateAPIView):
    """api view"""
    serializer_class = UserSerializer

class UserAuthTokenView(ObtainAuthToken):
    """auth token user view"""
    serializer_class = UserTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManagerUserApiView(generics.RetrieveUpdateAPIView):
    """manager user api view that retrive user profile"""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """retrive user detail"""
        return self.request.user