from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from rest_framework.authtoken.models import Token
from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.configuration_models import Scene, Outfit
from puppetshowapp.models.new_models import Performer


class UserEndpointTestCase(APITestCase):
    def setUp(self):
        normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="1234567890", discord_username="testuser"
        )
        normal_user_2 = DiscordPointingUser.objects.create(
            discord_snowflake="09876543210", discord_username="testuser_2"
        )

        scene_1 = Scene.objects.create(
            scene_author=normal_user_1, scene_name="test_scene"
        )
        scene_2 = Scene.objects.create(
            scene_author=normal_user_1, scene_name="test_scene_2", is_active=True
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

        self.token = Token.objects.create(user=normal_user_1)
        self.token_2 = Token.objects.create(user=normal_user_2)

        Outfit.objects.create(
            performer=performer_1, outfit_name="test_actor", scene=scene_1
        )
        Outfit.objects.create(
            performer=performer_2, outfit_name="test_actor_2", scene=scene_1
        )
        Outfit.objects.create(
            performer=performer_1, outfit_name="test_actor_3", scene=scene_2
        )

    # Test that the user can access their own user data.
    def test_user_get(self):
        client = APIClient()
        client.force_authenticate(token=self.token)
        url = reverse("user-info")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uuid"], str(self.token.user.uuid))
        self.assertEqual(response.data["discord_snowflake"], "1234567890")
        self.assertEqual(response.data["discord_username"], "testuser")
        self.assertEqual(response.data["scenes"][0]["scene_name"], "test_scene")
        self.assertEqual(response.data["active_scene"]["scene_name"], "test_scene_2")

    # Test that the user can update their own user data.
    def test_user_update(self):
        user = self.token.user
        client = APIClient()
        client.force_authenticate(token=self.token)
        url = reverse("user-info")
        response = client.patch(
            url,
            {"discord_snowflake": "1234567890", "discord_username": "testuser_69420"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uuid"], str(user.uuid))
        self.assertEqual(response.data["discord_snowflake"], "1234567890")
        self.assertEqual(response.data["discord_username"], "testuser_69420")
        self.assertEqual(
            DiscordPointingUser.objects.get(uuid=user.uuid).discord_username,
            "testuser_69420",
        )
        self.assertEqual(
            DiscordPointingUser.objects.get(
                discord_snowflake="09876543210"
            ).discord_username,
            "testuser_2",
        )

    # Test that user cannot update read-only fields.
    def test_user_update_readonly(self):
        user = self.token.user
        old_uuid = str(user.uuid)
        client = APIClient()
        client.force_authenticate(token=self.token)
        url = reverse("user-info")
        response = client.patch(
            url,
            {
                "discord_snowflake": "6969420",
                "uuid": "1234567890",
                "discord_username": "testuser_blehghghsgjhsg",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        updated_user = DiscordPointingUser.objects.get(uuid=old_uuid)
        response_dict = response.data
        self.assertEqual(response_dict["uuid"], old_uuid)
        self.assertEqual(response_dict["discord_snowflake"], "1234567890")
        self.assertEqual(response_dict["discord_username"], "testuser_blehghghsgjhsg")
        self.assertEqual(updated_user.discord_username, "testuser_blehghghsgjhsg")
        self.assertEqual(updated_user.discord_snowflake, "1234567890")
        self.assertEqual(str(updated_user.uuid), old_uuid)
