from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from rest_framework.authtoken.models import Token

from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.configuration_models import Scene, Outfit
from puppetshowapp.models.new_models import Performer
from puppetshowapp.constants import DEFAULT_OUTFIT_SETTINGS


# TODO rewrite, this should need a lot less code with the new functions.
class OutfitEndpointTestCase(APITestCase):
    def setUp(self):
        normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="1234567890"
        )
        normal_user_2 = DiscordPointingUser.objects.create(
            discord_snowflake="09876543210"
        )

        scene_1 = Scene.objects.create(
            scene_author=normal_user_1, scene_name="test_scene"
        )
        scene_2 = Scene.objects.create(
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

        token = Token.objects.create(user=normal_user_1)

    # Test that a user can create an outfit, and that the outfit has the correct properties.
    def test_create_outfit(self):
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        performer_1 = Performer.objects.get(parent_user=user_1)
        token = Token.objects.get(user=user_1)
        scene_1 = Scene.objects.filter(scene_author=user_1).first()
        url = reverse("outfit-list", args=[scene_1.identifier])
        client = APIClient()
        client.force_authenticate(token=token)
        outfit_data = {
            "outfit_name": "test_outfit",
            "performer_id": performer_1.identifier,
        }

        response = client.post(url, outfit_data, format="json")
        self.assertEqual(response.status_code, 201)

        response_dict = response.json()
        self.assertEqual(response_dict["outfit_name"], "test_outfit")
        self.assertEqual(response_dict["settings"], DEFAULT_OUTFIT_SETTINGS())
        self.assertIsNotNone(Outfit.objects.get(outfit_name="test_outfit"))

        created_outfit = Outfit.objects.get(outfit_name="test_outfit")
        self.assertEqual(created_outfit.performer.discord_snowflake, "6969420")
        self.assertEqual(
            Performer.objects.filter(discord_snowflake="6969420").count(), 1
        )

    # # Test that a a user can create an outfit based only on performer snowflake if the performer doesn't exist.
    # # NOT YET IMPLEMENTED
    # def test_create_outfit_with_performer_snowflake(self):
    #     client = APIClient()
    #     outfit_data = {
    #         "actor_name": "test_actor_2",
    #         "actor_base_user_id": "6969420",
    #     }
    #     response = client.post(url, outfit_data, format="json")
    #     # self.assertEqual(response.status_code, 201)
    #     # self.assertIsNotNone(response.content)
    #     # response_dict = response.json()
    #     # self.assertEqual(response_dict["actor_name"], "test_actor_2")
    #     # self.assertEqual(response_dict["settings"], DEFAULT_OUTFIT_SETTINGS())
    #     # self.assertIsNotNone(Outfit.objects.get(actor_name="test_actor_2"))
    #     # self.assertIsNotNone(DiscordData.objects.get(user_snowflake="6969420"))

    # # Make sure that a user can't access, edit, or delete another user's actor
    def test_get_outfit_for_other_user(self):
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        user_2 = DiscordPointingUser.objects.get(discord_snowflake="09876543210")
        performer_1 = Performer.objects.get(discord_snowflake="6969420")
        scene = Scene.objects.filter(scene_author=user_1).first()
        outfit_test = Outfit.objects.create(
            performer=performer_1, scene=scene, outfit_name="test_outfit_2"
        )

        url = reverse("outfit-detail", args=[outfit_test.identifier])
        client = APIClient()
        client.force_authenticate(user=user_2)
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        bad_put_data = {"actor_name": "hehehe get rekt"}
        response = client.put(url, bad_put_data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Outfit.objects.get(pk=outfit_test.pk).outfit_name, "test_outfit_2"
        )
        response = client.patch(url, bad_put_data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Outfit.objects.get(pk=outfit_test.pk).outfit_name, "test_outfit_2"
        )
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(Outfit.objects.get(pk=outfit_test.pk))

    # Make sure that a user can access their own outfits
    def test_get_outfit_for_self(self):
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        token_1 = Token.objects.get(user=user_1)
        performer_1 = Performer.objects.get(discord_snowflake="6969420")
        scene = Scene.objects.first()
        outfit_test = Outfit.objects.create(
            performer=performer_1, scene=scene, outfit_name="test_outfit_2"
        )

        url = reverse("outfit-detail", args=[outfit_test.identifier])
        client = APIClient()

        client.force_authenticate(token=token_1)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["outfit_name"], "test_outfit_2")

    # Make sure that a user can edit their outfit
    def test_edit_outfit(self):
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        token = Token.objects.get(user=user_1)
        performer_1 = Performer.objects.get(discord_snowflake="6969420")
        scene = Scene.objects.first()
        outfit_test = Outfit.objects.create(
            performer=performer_1, scene=scene, outfit_name="test_outfit_2"
        )
        url = reverse("outfit-detail", args=[outfit_test.identifier])
        client = APIClient()
        client.force_authenticate(token=token)
        patch_data = {"outfit_name": "test_outfit_3"}
        response = client.patch(url, patch_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        response_dict = response.json()
        self.assertEqual(response_dict["outfit_name"], "test_outfit_3")
        self.assertEqual(
            Outfit.objects.get(pk=outfit_test.pk).outfit_name, "test_outfit_3"
        )

    # Make sure that you can delete an outfit you own.
    def test_delete_outfit(self):
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        token = Token.objects.get(user=user_1)
        performer_1 = Performer.objects.get(discord_snowflake="6969420")
        scene = Scene.objects.first()
        outfit_test = Outfit.objects.create(
            performer=performer_1, scene=scene, outfit_name="test_outfit_2"
        )
        url = reverse("outfit-detail", args=[outfit_test.identifier])
        client = APIClient()
        client.force_authenticate(token=token)
        response = client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertRaises(Outfit.DoesNotExist, Outfit.objects.get, pk=outfit_test.pk)
