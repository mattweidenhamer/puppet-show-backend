from ..models.configuration_models import Outfit, Scene
from ..serializers import *
from ..permissions import IsObjectOwner, HasValidToken

from django.http import JsonResponse, Http404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


class SceneList(generics.ListCreateAPIView):
    # Query all the scenes that the user has created.
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken]
    serializer_class = SceneSerializer
    lookup_field = "identifier"

    def get_queryset(self):
        token = self.request.auth
        user = Token.objects.get(key=token).user
        return Scene.objects.filter(scene_author=user)

    def perform_create(self, serializer):
        token = self.request.auth
        user = Token.objects.get(key=token).user
        serializer.save(scene_author=user)


class SceneDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken, IsObjectOwner]
    serializer_class = SceneSerializer
    queryset = Scene.objects.all()
    lookup_field = "identifier"


class ActiveScene(generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken]
    serializer_class = SceneSerializer
    lookup_field = "identifier"

    def get_object(self):
        token = self.request.auth
        user = Token.objects.get(key=token).user
        active_scene = user.active_scene
        if active_scene is None:
            raise Http404

        return active_scene


class OutfitList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken]
    serializer_class = OutfitSerializer
    # Query all the actors in the provided scene.

    def get_queryset(self):
        return Outfit.objects.filter(scene__identifier=self.kwargs["identifier"])

    def perform_create(self, serializer):
        token = self.request.auth
        user = Token.objects.get(key=token).user
        if not serializer.is_valid():
            return JsonResponse(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": f"Invalid data: {serializer.errors}"},
            )
        scene = Scene.objects.get(identifier=self.kwargs["identifier"])
        if scene.scene_author != user:
            return JsonResponse(
                status=status.HTTP_403_FORBIDDEN,
                data={"message": "You are not the author of this outfit."},
            )
        serializer.save(scene=scene)


class OutfitDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken, IsObjectOwner]
    queryset = Outfit.objects.all()
    serializer_class = OutfitSerializer
    lookup_field = "identifier"


class PerformerList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken]
    serializer_class = PerformerSerializer

    def get_queryset(self):
        token = self.request.auth
        user = Token.objects.get(key=token).user
        return Performer.objects.filter(parent_user=user)

    def perform_create(self, serializer):
        token = self.request.auth
        user = Token.objects.get(key=token).user
        if serializer.is_valid():
            try:
                # See if there is already a performer by this user with the same snowflake.
                performer = Performer.objects.get(
                    parent_user__discord_snowflake=user.discord_snowflake,
                    discord_snowflake=serializer.validated_data["discord_snowflake"],
                )
                return JsonResponse(
                    status=status.HTTP_409_CONFLICT,
                    data={
                        "message": "Performer with that snowflake already exists under this account."
                    },
                )
            except Performer.DoesNotExist:
                pass
            serializer.save(parent_user=user)


class PerformerDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken, IsObjectOwner]
    queryset = Performer.objects.all()
    serializer_class = PerformerSerializer
    lookup_field = "identifier"


class PerformanceView(generics.RetrieveAPIView):
    queryset = Performer.objects.all()
    serializer_class = StageSerializer
    lookup_field = "identifier"


class PerformanceSpecificOutfitView(generics.RetrieveAPIView):
    queryset = Performer.objects.all()
    serializer_class = StageSerializerCustomOutfit
    lookup_field = "identifier"

    def get(self, request, identifier, outfit_identifier):
        if not identifier or not outfit_identifier:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Both identifiers are required."},
            )
        try:
            performer = Performer.objects.get(identifier=identifier)
            outfit = Outfit.objects.get(identifier=outfit_identifier)
        except Performer.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Performer not found."},
            )
        except Outfit.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Outfit not found."},
            )
        if outfit.get_owner != performer.parent_user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"message": "Outfit does not belong to this performer."},
            )
        outfit_obj = Outfit.objects.get(identifier=outfit_identifier)
        serializer = self.serializer_class(performer, context={"outfit": outfit_obj})
        # Change the get_outfit value of the serializer to the passed outfit
        # if not serializer.is_valid():
        #     return Response(
        #         status=status.HTTP_400_BAD_REQUEST,
        #         data={"message": f"Invalid data: {serializer.errors}"},
        #     )
        return Response(serializer.data)


class SetActiveScene(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken]
    queryset = Scene.objects.all()
    serializer_class = SceneSerializer
    lookup_field = "identifier"

    def create(self, request, *args, **kwargs):
        token = self.request.auth
        user = Token.objects.get(key=token).user
        scene = self.get_object()
        if scene.scene_author != user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"message": "You are not the author of this scene."},
            )
        scene.set_active()
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Active scene set."},
        )


class CreateAnimation(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken]
    serializer_class = AnimationSerializer


class ModifyAnimation(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasValidToken, IsObjectOwner]
    serializer_class = AnimationSerializer
    queryset = Animation.objects.all()
    lookup_field = "identifier"
