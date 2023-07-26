from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from rest_framework.authtoken.models import Token

from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.configuration_models import Scene, Outfit
from puppetshowapp.models.new_models import Performer
from puppetshowapp.constants import DEFAULT_SCENE_SETTINGS


class SceneEndpointTestCase(APITestCase):
    def setUp(self):
        normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="1234567890",
        )
        normal_user_2 = DiscordPointingUser.objects.create(
            discord_snowflake="09876543210",
        )

        self.scene_1 = Scene.objects.create(
            scene_author=normal_user_1, scene_name="test_scene"
        )
        self.scene_2 = Scene.objects.create(
            scene_author=normal_user_1, scene_name="test_scene_2"
        )
        performer_1 = Performer.objects.create(
            parent_user=normal_user_1,
            discord_username="test_performer",
            discord_snowflake="6969420",
        )
        performer_2 = Performer.objects.create(
            parent_user=normal_user_2,
            discord_username="test_performer_2",
            discord_snowflake="112345689101122",
        )
        outfit_1 = Outfit.objects.create(
            performer=performer_1, outfit_name="test_actor", scene=self.scene_1
        )
        outfit_2 = Outfit.objects.create(
            performer=performer_2, outfit_name="test_actor_2", scene=self.scene_1
        )
        outfit_3 = Outfit.objects.create(
            performer=performer_1, outfit_name="test_actor_3", scene=self.scene_2
        )
        token = Token.objects.create(user=normal_user_1)
        token_2 = Token.objects.create(user=normal_user_2)

    # Test that users can create a scene, and that the scene has the correct properties.
    def test_create_scene(self):
        token = Token.objects.get(user__discord_snowflake="09876543210")
        user_2 = DiscordPointingUser.objects.get(discord_snowflake="09876543210")
        url = reverse("scene-list")
        client = APIClient()
        client.force_authenticate(token=token)
        data = {"scene_name": "test_scene_100"}

        response = client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Scene.objects.filter(scene_name="test_scene_100").count(), 1)
        createdScene = Scene.objects.filter(scene_name="test_scene_100").first()
        self.assertEqual(createdScene.get_owner, user_2)
        self.assertEqual(createdScene.scene_name, "test_scene_100")

    # Make sure that a user can't access, edit, or delete another user's scene
    def test_get_scene_for_other_user(self):
        token_2 = Token.objects.get(user__discord_snowflake="09876543210")
        token = Token.objects.get(user__discord_snowflake="1234567890")
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        user_2 = DiscordPointingUser.objects.get(discord_snowflake="09876543210")
        scene_1 = self.scene_1
        url = reverse("scene-detail", args=[scene_1.identifier])
        client = APIClient()
        client.force_authenticate(token=token)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        client.force_authenticate(token=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 401)
        client.force_authenticate(token=token_2)
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        modified_data = {"scene_name": "test_scene_69"}
        response = client.put(url, modified_data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Scene.objects.filter(scene_name="test_scene_69").count(), 0)
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Scene.objects.filter(scene_name="test_scene").count(), 1)

    # Make sure that a user can access, modify, and delete their own scene
    def test_view_scene_for_self(self):
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        token = Token.objects.get(user=user_1)
        scene_1 = self.scene_1
        url = reverse("scene-detail", args=[scene_1.identifier])
        client = APIClient()
        client.force_authenticate(token=token)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["scene_name"], "test_scene")
        self.assertEqual(response_dict["is_active"], False)
        self.assertEqual(response_dict["scene_settings"], DEFAULT_SCENE_SETTINGS())
        self.assertEqual(len(response_dict["outfits"]), 2)
        self.assertEqual(response_dict["outfits"][0]["outfit_name"], "test_actor")
        self.assertEqual(response_dict["outfits"][1]["outfit_name"], "test_actor_2")

        modified_data = {"scene_name": "test_scene_69"}
        response = client.patch(url, modified_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Scene.objects.filter(scene_name="test_scene_69").count(), 1)
        self.assertEqual(Scene.objects.filter(scene_name="test_scene").count(), 0)
        response = client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Scene.objects.filter(scene_name="test_scene_69").count(), 0)

    # Make sure that a user can access a list of all of their scenes
    def test_retrieve_scene_list(self):
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        token = Token.objects.get(user=user_1)
        url = reverse("scene-list")
        client = APIClient()
        client.force_authenticate(token=token)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(len(response_dict), 2)
        self.assertEqual(response_dict[0]["scene_name"], "test_scene")
        self.assertEqual(response_dict[1]["scene_name"], "test_scene_2")
        user_2 = DiscordPointingUser.objects.get(discord_snowflake="09876543210")
        token_2 = Token.objects.get(user=user_2)
        client.force_authenticate(token=token_2)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(len(response_dict), 0)
        client.force_authenticate(user=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

    # Make sure that you can get a user's active scene.
    def test_get_active_scene(self):
        scene_1 = Scene.objects.get(scene_name="test_scene")
        scene_1.set_active()
        scene_1.save()
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        token = Token.objects.get(user=user_1)
        url = reverse("scene-active")
        client = APIClient()
        client.force_authenticate(token=token)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["scene_name"], "test_scene")

    # Test that a scene returns a proper animation for its preview image.
    # def test_get_scene_preview(self):
    #     scene_1 = Scene.objects.get(scene_name="test_scene")
    #     scene_1.set_active()
    #     scene_1.save()
    #     user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
    #     token = Token.objects.get(user=user_1)
    #     url = reverse("scene-detail", args=[scene_1.identifier])
    #     client = APIClient()
    #     client.force_authenticate(token=token)
    #     response = client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNotNone(response.content)
    #     response_dict = response.json()
    #     self.assertEqual(response_dict["scene_name"], "test_scene")
    #     self.assertEqual(response_dict["preview_image"], scene_1.preview_image)

    # Test that a scene's settings can be updated.
    def test_update_scene_settings(self):
        raise NotImplementedError


class ChangeSceneEndpointTestCase(APITestCase):
    def setUp(self):
        self.normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="1234567890"
        )
        self.normal_user_2 = DiscordPointingUser.objects.create(
            discord_snowflake="09876543210"
        )

        self.scene_1 = Scene.objects.create(
            scene_author=self.normal_user_1, scene_name="test_scene", is_active=True
        )
        self.scene_2 = Scene.objects.create(
            scene_author=self.normal_user_1, scene_name="test_scene_2"
        )
        self.scene_3 = Scene.objects.create(
            scene_author=self.normal_user_2, scene_name="test_scene_3"
        )
        self.performer_1 = Performer.objects.create(
            parent_user=self.normal_user_1,
            discord_username="test_performer",
            discord_snowflake="6969420",
        )
        self.performer_2 = Performer.objects.create(
            parent_user=self.normal_user_2,
            discord_username="test_performer_2",
            discord_snowflake="112345689101122",
        )
        self.token_1 = Token.objects.create(user=self.normal_user_1)
        self.token_2 = Token.objects.create(user=self.normal_user_2)

    # Make sure that a user can change their active scene.
    def test_change_scene(self):
        url = reverse("set-active-scene", args=[self.scene_1.identifier])
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        response = client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            DiscordPointingUser.objects.get(pk=self.normal_user_1.pk).active_scene.pk,
            self.scene_1.pk,
        )
        self.assertEqual(Scene.objects.get(pk=self.scene_1.pk).is_active, True)
        self.assertEqual(Scene.objects.get(pk=self.scene_2.pk).is_active, False)
        url = reverse("set-active-scene", args=[self.scene_2.pk])
        response = client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            DiscordPointingUser.objects.get(pk=self.normal_user_1.pk).active_scene.pk,
            self.scene_2.pk,
        )
        self.assertEqual(Scene.objects.get(pk=self.scene_1.pk).is_active, False)
        self.assertEqual(Scene.objects.get(pk=self.scene_2.pk).is_active, True)

        client.force_authenticate(token=self.token_2)
        url = reverse("set-active-scene", args=[self.scene_2.pk])
        response = client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            DiscordPointingUser.objects.get(pk=self.normal_user_1.pk).active_scene.pk,
            self.scene_2.pk,
        )
        self.assertEqual(Scene.objects.get(pk=self.scene_1.pk).is_active, False)
        self.assertEqual(Scene.objects.get(pk=self.scene_2.pk).is_active, True)
