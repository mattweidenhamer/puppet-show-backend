from django.test import TestCase
from puppetshowapp.models.configuration_models import Outfit, Scene
from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.new_models import Performer


class SceneTestCase(TestCase):
    # Create Actor objects and their scenes, make sure they are correctly saved
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
            parent_user=normal_user_1, discord_snowflake="1653402"
        )
        performer_2 = Performer.objects.create(
            parent_user=normal_user_2, discord_snowflake="72645372"
        )

        Outfit.objects.create(
            performer=performer_1, outfit_name="test_actor", scene=scene_1
        )
        Outfit.objects.create(
            performer=performer_2, outfit_name="test_actor_2", scene=scene_1
        )
        Outfit.objects.create(
            performer=performer_2, outfit_name="test_actor_3", scene=scene_2
        )

    # Make sure that the Scene objects are correctly linked to the Actor objects
    def test_actor_link(self):
        actor_1 = Outfit.objects.get(outfit_name="test_actor")
        actor_2 = Outfit.objects.get(outfit_name="test_actor_2")

        scene_1 = Scene.objects.get(scene_name="test_scene")

        self.assertEqual(actor_1.scene, scene_1)
        self.assertEqual(actor_2.scene, scene_1)

    # Make sure that the scene objects are correctly linked to their user
    def test_user_link(self):
        scene_1 = Scene.objects.get(scene_name="test_scene")
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")

        self.assertEqual(scene_1.scene_author, user_1)
