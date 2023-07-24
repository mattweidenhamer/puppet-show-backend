from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from rest_framework.authtoken.models import Token

from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.configuration_models import Scene, Outfit
from puppetshowapp.models.new_models import Performer
from puppetshowapp.models.data_models import Animation


class AnimationTestCase(APITestCase):
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

    # Test that the outfit model returns a list of its animations
    def test_outfit_animations(self):
        url = reverse("outfit-detail", kwargs={"identifier": self.outfit.identifier})
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["animations"]), 0)
        animation_1 = Animation.objects.create(
            outfit=self.outfit,
            animation_type="START_SPEAKING",
            animation_path="https://media.discordapp.net/attachments/807108520595554304/1022846319825539072/Tair_Speak.gif",
        )
        animation_2 = Animation.objects.create(
            outfit=self.outfit,
            animation_type="STOP_SPEAKING",
            animation_path="https://media.discordapp.net/attachments/807108520595554304/1022846320253353984/Tair_Mute.gif",
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["animations"]), 2)
        self.assertEqual(
            response.json()["animations"][0]["animation_type"], "START_SPEAKING"
        )
        self.assertEqual(
            response.json()["animations"][1]["animation_type"], "STOP_SPEAKING"
        )

    # Test creating an animation based on the outfit's identifier.
    def test_create_animation(self):
        url = reverse("animations-create")
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        new_animation = {
            "outfit_identifier": self.outfit.identifier,
            "animation_type": "START_SPEAKING",
            "animation_path": "https://media.discordapp.net/attachments/807108520595554304/1022846319825539072/Tair_Speak.gif",
        }
        new_animation_2 = {
            "outfit_identifier": self.outfit.identifier,
            "animation_type": "NOT_SPEAKING",
            "animation_path": "https://media.discordapp.net/attachments/807108520595554304/1022846320253353984/Tair_Mute.gif",
        }
        response = client.post(url, new_animation)
        # self.assertIsNone(response.json())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.outfit.animations.count(), 1)
        self.assertEqual(response.json()["animation_type"], "START_SPEAKING")
        self.assertEqual(
            response.json()["animation_path"], new_animation["animation_path"]
        )
        response = client.post(url, new_animation_2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.outfit.animations.count(), 2)
        self.assertEqual(response.json()["animation_type"], "NOT_SPEAKING")

    # Test modifying an animation's path.
    def test_modify_animation(self):
        animation = Animation.objects.create(
            outfit=self.outfit,
            animation_type="START_SPEAKING",
            animation_path="https://media.discordapp.net/attachments/807108520595554304/1022846319825539072/Tair_Speak.gif",
        )
        url = reverse("animations-modify", kwargs={"identifier": animation.identifier})
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        new_animation = {
            "outfit_identifier": self.outfit.identifier,
            "animation_type": "START_SPEAKING",
            "animation_path": "https://media.discordapp.net/attachments/807108520595554304/1022846319825539072/Tair_Speak.gif",
        }
        response = client.patch(url, new_animation)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.outfit.animations.count(), 1)
        self.assertEqual(response.json()["animation_type"], "START_SPEAKING")
        self.assertEqual(
            response.json()["animation_path"], new_animation["animation_path"]
        )

    # Test deleting an animation.
    def test_delete_animation(self):
        animation = Animation.objects.create(
            outfit=self.outfit,
            animation_type="START_SPEAKING",
            animation_path="https://media.discordapp.net/attachments/807108520595554304/1022846319825539072/Tair_Speak.gif",
        )
        url = reverse("animations-modify", kwargs={"identifier": animation.identifier})
        client = APIClient()
        client.force_authenticate(token=self.token_1)
        response = client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.outfit.animations.count(), 0)
