from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models.configuration_models import Outfit, Scene
from ..models.authentication_models import DiscordPointingUser
from ..models.data_models import Animation
from ..models.new_models import Performer
import os

TEST_FOLDER_LOCATION = os.path.join(os.path.dirname(__file__), "static_test_files")


# class DataTestCase(TestCase):
#     # Create DiscordData objects and make sure they are correctly saved
#     def setUp(self):
#         DiscordData.objects.create(
#             user_snowflake="1234567890", user_username="testuser"
#         )
#         DiscordData.objects.create(
#             user_snowflake="09876543210", user_username="testuser_2"
#         )

#     def test_creation(self):
#         data_1 = DiscordData.objects.get(user_snowflake="1234567890")
#         data_2 = DiscordData.objects.get(user_snowflake="09876543210")

#         self.assertEqual(data_1.user_username, "testuser")
#         self.assertEqual(data_2.user_username, "testuser_2")


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


class PerformerTestCase(TestCase):
    def setUp(self):
        normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="1234567890"
        )
        normal_user_2 = DiscordPointingUser.objects.create(
            discord_snowflake="09876543210"
        )

        scene_1 = Scene.objects.create(
            scene_author=normal_user_1, scene_name="test_scene", is_active=True
        )
        scene_2 = Scene.objects.create(
            scene_author=normal_user_1, scene_name="test_scene_2"
        )

        performer_1 = Performer.objects.create(
            parent_user=normal_user_1, discord_snowflake="1653402"
        )
        performer_2 = Performer.objects.create(
            parent_user=normal_user_1, discord_snowflake="72645372"
        )
        performer_3 = Performer.objects.create(
            parent_user=normal_user_2, discord_snowflake="72645373"
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

    # Test that performers can retrieve the users they're linked to.
    def test_user_link(self):
        performer_1 = Performer.objects.get(discord_snowflake="1653402")
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")

        self.assertEqual(performer_1.parent_user, user_1)

    # Ttest that users can retrieve the performers they've set up.
    def test_performer_link(self):
        performer_1 = Performer.objects.get(discord_snowflake="1653402")
        user_1 = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        user_2 = DiscordPointingUser.objects.get(discord_snowflake="09876543210")

        self.assertTrue(performer_1 in user_1.added_performers.all())
        self.assertEqual(user_1.added_performers.count(), 2)
        self.assertEqual(user_2.added_performers.count(), 1)

    # Test that performers will retrieve the correct outfit for their owner's current scene.
    def test_performer_outfit(self):
        performer_1 = Performer.objects.get(discord_snowflake="1653402")
        performer_2 = Performer.objects.get(discord_snowflake="72645372")
        performer_3 = Performer.objects.get(discord_snowflake="72645373")

        scene_1 = Scene.objects.get(scene_name="test_scene")
        scene_2 = Scene.objects.get(scene_name="test_scene_2")

        outfit_1 = Outfit.objects.get(outfit_name="test_actor")
        outfit_2 = Outfit.objects.get(outfit_name="test_actor_2")
        outfit_3 = Outfit.objects.get(outfit_name="test_actor_3")

        self.assertEqual(performer_1.get_outfit, outfit_1)
        self.assertEqual(performer_2.get_outfit, outfit_2)
        self.assertEqual(performer_3.get_outfit, None)
        scene_1.is_active = False
        scene_1.save()
        scene_2.is_active = True
        scene_2.save()
        self.assertEqual(performer_2.get_outfit, outfit_3)
        self.assertEqual(performer_1.get_outfit, None)
        # TODO change so that if a performer has no outfit, it will return their avatar.
