from .serializers import UserSerializer
from .models import DiscordPointingUser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters

class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated"]
    ordering = ["-updated"]

    def get_queryset(self):
        pass