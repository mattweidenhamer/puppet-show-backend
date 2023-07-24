from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from rest_framework.authtoken.models import Token
from unittest.mock import MagicMock, Mock, patch
import requests

from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.configuration_models import Scene, Outfit
from puppetshowapp.models.new_models import Performer

from puppetshowapp.secrets.test_raw import RAW_ME, FAKE_RAW_TOKEN


class StageEndpointTestCase(APITestCase):
    def setUp(self):
        self.user = DiscordPointingUser.objects.create(
            discord_snowflake="1234567890", discord_username="test_user"
        )
        self.user_2 = DiscordPointingUser.objects.create(
            discord_snowflake="09876543210", discord_username="test_user_2"
        )
        self.performer = Performer.objects.create(
            discord_snowflake="6969420",
            discord_username="test_performer",
            parent_user=self.user,
        )
        self.performer_2 = Performer.objects.create(
            discord_snowflake="6969421",
            discord_username="test_performer_2",
            parent_user=self.user_2,
        )
        self.scene_1 = Scene.objects.create(
            scene_author=self.user, scene_name="test_scene_1", is_active=True
        )
        self.scene_2 = Scene.objects.create(
            scene_author=self.user, scene_name="test_scene_2"
        )
        self.outfit = Outfit.objects.create(
            performer=self.performer, scene=self.scene_2, outfit_name="test_outfit"
        )
        self.outfit_2 = Outfit.objects.create(
            performer=self.performer_2, scene=self.scene_2, outfit_name="test_outfit_2"
        )
        self.outfit_3 = Outfit.objects.create(
            performer=self.performer, scene=self.scene_1, outfit_name="test_outfit_3"
        )
        self.outfit_4 = Outfit.objects.create(
            performer=self.performer_2, scene=self.scene_1, outfit_name="test_outfit_4"
        )
        self.token_1 = Token.objects.create(user=self.user)
        self.token_2 = Token.objects.create(user=self.user_2)

    # Make sure that anyone, including anonymous users, can access a stage.
    def test_get_stage(self):
        url = reverse("stage-performance", args=[self.performer.identifier])
        client = APIClient()
        client.force_authenticate(token=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["discord_snowflake"], "6969420")
        self.assertEqual(response_dict["get_outfit"]["outfit_name"], "test_outfit_3")
        client.force_authenticate(token=self.token_1)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["discord_snowflake"], "6969420")
        self.assertEqual(response_dict["get_outfit"]["outfit_name"], "test_outfit_3")
        client.force_authenticate(token=self.token_2)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["discord_snowflake"], "6969420")
        self.assertEqual(response_dict["get_outfit"]["outfit_name"], "test_outfit_3")

    # Make sure that stages cannot be directly modified.
    def test_modify_stage(self):
        url = reverse("stage-performance", args=[self.performer.identifier])
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.put(url, {}, format="json")
        self.assertEqual(response.status_code, 405)
        response = client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, 405)

    # Make sure that the outfit returned changes when the creating user's active scene changes.
    def test_performer_outfits_change_on_scene_change(self):
        url = reverse("stage-performance", args=[self.performer.identifier])
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["get_outfit"]["outfit_name"], "test_outfit_3")
        self.scene_2.set_active()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["get_outfit"]["outfit_name"], "test_outfit")


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


class MockDiscordTokenCallback:
    def raise_for_status(self):
        pass

    def json(self):
        return FAKE_RAW_TOKEN


class MockDiscordMeCallback:
    def raise_for_status(self):
        pass

    def json(self):
        return RAW_ME


class TokenExchangeTestCase(APITestCase):
    def setUp(self):
        self.mock_discord_token_callback = MagicMock()
        self.mock_discord_token_callback.raise_for_status = Mock(return_value=None)
        self.mock_discord_token_callback.json = Mock(return_value=FAKE_RAW_TOKEN)
        self.mock_discord_me_callback = MagicMock()
        self.mock_discord_me_callback.raise_for_status = Mock(return_value=None)
        self.mock_discord_me_callback.json = Mock(return_value=RAW_ME)
        self.mock_bad_callback = MagicMock()
        self.raise_for_status = Mock(side_effect=requests.HTTPError("Bad request"))

    # Test that when sending a user token to the endpoint, it authenticates via discord and returns a token.
    def test_token_exchange_existing(self):
        normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="249615304185872395"
        )

        with patch("requests.post", return_value=self.mock_discord_token_callback):
            with patch("requests.get", return_value=self.mock_discord_me_callback):
                url = reverse("token-exchange")
                client = APIClient()
                response = client.get(url, {"code": "test_token"})
        self.assertEqual(response.status_code, 302)
        updated_normal_user = DiscordPointingUser.objects.get(pk=normal_user_1.pk)
        self.assertEqual(
            updated_normal_user.discord_auth_token, FAKE_RAW_TOKEN["access_token"]
        )
        self.assertEqual(
            updated_normal_user.discord_refresh_token, FAKE_RAW_TOKEN["refresh_token"]
        )
        token = response.url.split("token=")[1]
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.get(reverse("user-info"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["discord_snowflake"], "249615304185872395")

    # Same as the above test, but the user doesn't exist in the database and should be created.
    def test_token_withuser(self):
        with patch("requests.post", return_value=self.mock_discord_token_callback):
            with patch("requests.get", return_value=self.mock_discord_me_callback):
                url = reverse("token-exchange")
                client = APIClient()
                response = client.get(url, {"code": "test_token"})
        self.assertEqual(response.status_code, 302)
        updated_normal_user = DiscordPointingUser.objects.get(
            discord_snowflake="249615304185872395"
        )
        self.assertEqual(
            updated_normal_user.discord_auth_token, FAKE_RAW_TOKEN["access_token"]
        )
        self.assertEqual(
            updated_normal_user.discord_refresh_token, FAKE_RAW_TOKEN["refresh_token"]
        )
        token = response.url.split("token=")[1]
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.get(reverse("user-info"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["discord_snowflake"], "249615304185872395")

    # Test that the endpoint returns a 400 error if the token is invalid or expired.
    def test_token_invalid(self):
        with patch("requests.post", return_value=self.mock_bad_callback):
            url = reverse("token-exchange")
            client = APIClient()
            response = client.get(url, {"code": "test_token"})
        self.assertEqual(response.status_code, 400)
