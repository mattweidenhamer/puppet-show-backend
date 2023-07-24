from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from rest_framework.authtoken.models import Token

from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.configuration_models import Scene, Outfit
from puppetshowapp.models.new_models import Performer


class PerformerEndpointTestCase(APITestCase):
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
            scene_author=self.user, scene_name="test_scene_1"
        )
        self.scene_2 = Scene.objects.create(
            scene_author=self.user, scene_name="test_scene"
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

    # Make sure that a user can access their own performers
    def test_get_performer_for_self(self):
        url = reverse("performer-detail", args=[self.performer.pk])
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["discord_username"], "test_performer")

    # Make sure that a user can't access, edit, or delete another user's performer
    def test_get_performer_for_other_user(self):
        url = reverse("performer-detail", args=[self.performer_2.pk])
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        bad_put_data = {"discord_username": "hehehe get rekt"}
        response = client.put(url, bad_put_data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Performer.objects.get(pk=self.performer_2.pk).discord_username,
            "test_performer_2",
        )
        response = client.patch(url, bad_put_data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Performer.objects.get(pk=self.performer_2.pk).discord_username,
            "test_performer_2",
        )
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(Performer.objects.get(pk=self.performer_2.pk))

    # Make sure that a user can add their own performer.
    def test_add_performer_for_self(self):
        url = reverse("performer-list")
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        good_post_data = {
            "discord_snowflake": "6969422",
        }
        response = client.post(url, good_post_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(
            response_dict["parent_user_snowflake"], self.user.discord_snowflake
        )
        self.assertEqual(response_dict["discord_snowflake"], "6969422")

    # Make sure that a user can change the settings of their performer.
    def test_change_performer_for_self(self):
        url = reverse("performer-detail", args=[self.performer.identifier])
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        good_put_data = {
            "discord_snowflake": self.performer.discord_snowflake,
            "settings": {"test_setting": "test_value"},
        }
        response = client.put(url, good_put_data, format="json")
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertEqual(response_dict["settings"], {"test_setting": "test_value"})
        self.assertEqual(
            Performer.objects.get(identifier=self.performer.identifier).settings,
            {"test_setting": "test_value"},
        )
