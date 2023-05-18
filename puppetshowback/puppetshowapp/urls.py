from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from .views import authentication_views, model_views, user_views

# router = routers.DefaultRouter()
# router.register(r"actors", views.ActorViewSet)
# router.register(r"scenes", views.SceneViewSet)
# router.register(r"users", views.UserViewSet)
# router.register(r"discorddata", views.DiscordDataViewSet)


urlpatterns = [
    path("user/", user_views.UserInfo.as_view(), name="user-info"),
    path("scenes/", model_views.SceneList.as_view(), name="scene-list"),
    path("scenes/active/", model_views.ActiveScene.as_view(), name="scene-active"),
    path(
        "scenes/<uuid:identifier>/",
        model_views.SceneDetail.as_view(),
        name="scene-detail",
    ),
    path(
        "scenes/<uuid:identifier>/outfits/",
        model_views.OutfitList.as_view(),
        name="outfit-list",
    ),
    path(
        "outfits/<uuid:identifier>/",
        model_views.OutfitDetail.as_view(),
        name="outfit-detail",
    ),
    path(
        "animations/",
        model_views.CreateAnimation.as_view(),
        name="animations-create",
    ),
    path(
        "animations/<uuid:identifier>/",
        model_views.ModifyAnimation.as_view(),
        name="animations-modify",
    ),
    path(
        "performers/",
        model_views.PerformerList.as_view(),
        name="performer-list",
    ),
    path(
        "performers/<uuid:identifier>/",
        model_views.PerformerDetail.as_view(),
        name="performer-detail",
    ),
    # TODO not restful
    path(
        "scenes/<uuid:identifier>/setActive/",
        model_views.SetActiveScene.as_view(),
        name="set-active-scene",
    ),
    path(
        "stage/<uuid:identifier>/",
        model_views.PerformanceView.as_view(),
        name="stage-performance",
    ),
]
