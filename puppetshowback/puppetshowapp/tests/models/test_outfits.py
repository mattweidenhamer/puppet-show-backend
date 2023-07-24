from django.test import TestCase
from puppetshowapp.models.configuration_models import Outfit, Scene
from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.data_models import Animation
from puppetshowapp.models.new_models import Performer
import os

TEST_FOLDER_LOCATION = os.path.join(os.path.dirname(__file__), "static_test_files")


class OutfitTestCase(TestCase):
    # Create Actor objects and their scenes, make sure they are correctly saved
    def setUp(self):
        normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="1234567890",
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

        outfit_1 = Outfit.objects.create(
            performer=performer_1, outfit_name="test_actor", scene=scene_1
        )
        outfit_2 = Outfit.objects.create(
            performer=performer_2, outfit_name="test_actor_2", scene=scene_1
        )
        outfit_3 = Outfit.objects.create(
            performer=performer_2, outfit_name="test_actor_3", scene=scene_2
        )
        Animation.objects.create(
            outfit=outfit_1,
            animation_type="START_SPEAKING",
            animation_path="https://www.google.com",
        )
        Animation.objects.create(
            outfit=outfit_1,
            animation_type="NOT_SPEAKING",
            animation_path="https://www.aol.com",
        )
        Animation.objects.create(
            outfit=outfit_2,
            animation_type="START_SPEAKING",
            animation_path="https://www.github.com",
        )
        Animation.objects.create(
            outfit=outfit_2,
            animation_type="NOT_SPEAKING",
            animation_path="https://www.teardown.com",
        )
        Animation.objects.create(
            outfit=outfit_3,
            animation_type="START_SPEAKING",
            animation_path="https://www.wowie.com",
        )
        Animation.objects.create(
            outfit=outfit_3,
            animation_type="NOT_SPEAKING",
            animation_path="https://www.whatdeheck.com",
        )

    # Make sure that the Outfit objects are correctly linked to the Scene objects
    def test_scene_link(self):
        outfit_1 = Outfit.objects.get(outfit_name="test_actor")
        outfit_2 = Outfit.objects.get(outfit_name="test_actor_2")

        scene_1 = Scene.objects.get(scene_name="test_scene")

        self.assertEqual(outfit_1.scene, scene_1)
        self.assertEqual(outfit_2.scene, scene_1)

    # Make sure that you can access the url of the outfit animation
    def test_image_data(self):
        outfit_1 = Outfit.objects.get(outfit_name="test_actor")
        outfit_2 = Outfit.objects.get(outfit_name="test_actor_2")
        outfit_3 = Outfit.objects.get(outfit_name="test_actor_3")

        self.assertEqual(outfit_1.getImage("START_SPEAKING"), "https://www.google.com")
        self.assertEqual(outfit_1.getImage("NOT_SPEAKING"), "https://www.aol.com")
        self.assertEqual(outfit_2.getImage("START_SPEAKING"), "https://www.github.com")
        self.assertEqual(outfit_2.getImage("NOT_SPEAKING"), "https://www.teardown.com")
        self.assertEqual(outfit_3.getImage("START_SPEAKING"), "https://www.wowie.com")
        self.assertEqual(
            outfit_3.getImage("NOT_SPEAKING"), "https://www.whatdeheck.com"
        )

        self.assertIn(
            outfit_3.getFirstImage(),
            ["https://www.wowie.com", "https://www.whatdeheck.com"],
        )
        self.assertIn(
            outfit_1.getFirstImage(),
            ["https://www.google.com", "https://www.aol.com"],
        )
        self.assertIn(
            outfit_2.getFirstImage(),
            ["https://www.github.com", "https://www.teardown.com"],
        )
