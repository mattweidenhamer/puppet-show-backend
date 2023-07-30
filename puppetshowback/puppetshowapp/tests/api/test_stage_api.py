from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from rest_framework.authtoken.models import Token

from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.configuration_models import Scene, Outfit
from puppetshowapp.models.new_models import Performer
import uuid


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
        client.force_authenticate(token=self.token_1)
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

    # Make sure that a user can access a stage with a specific, hardcoded outfit.
    def test_get_stage_with_specific_outfit(self):
        url = reverse(
            "stage-performance-specific-outfit",
            args=[self.performer.identifier, self.outfit.identifier],
        )
        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["discord_snowflake"], "6969420")
        self.assertEqual(response_dict["get_outfit"]["outfit_name"], "test_outfit")
        # Check to make sure that a user cant access an outfit of another performer.
        url = reverse(
            "stage-performance-specific-outfit",
            args=[self.performer_2.identifier, self.outfit_3.identifier],
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["message"], "Outfit does not belong to this performer."
        )
        # Check to make sure that a user cant access an outfit that doesn't exist.
        url = reverse(
            "stage-performance-specific-outfit",
            args=[self.performer.identifier, uuid.uuid4()],
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["message"], "Outfit not found.")
        # Check to make sure that a user cant access a performer that doesn't exist.
        url = reverse(
            "stage-performance-specific-outfit",
            args=[uuid.uuid4(), self.outfit.identifier],
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["message"], "Performer not found.")
