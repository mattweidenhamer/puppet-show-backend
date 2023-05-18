from ..models.authentication_models import DiscordPointingUser
from ..serializers import UserSerializer
from ..permissions import HasValidToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from rest_framework import generics


class UserInfo(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken]
    serializer_class = UserSerializer

    def get_object(self):
        token = self.request.auth
        user = Token.objects.get(key=token).user
        return user
