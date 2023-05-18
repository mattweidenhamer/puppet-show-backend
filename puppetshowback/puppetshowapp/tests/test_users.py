from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models.authentication_models import DiscordPointingUser
from ..models.configuration_models import Scene, Outfit
from ..models.new_models import Performer


class UserTestCase(TestCase):
    def setUp(self):
        normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="1234567890"
        )
        normal_user_2 = DiscordPointingUser.objects.create(
            discord_snowflake="1234567891"
        )
        superuser = DiscordPointingUser.objects.create_superuser(
            discord_snowflake="1234567899999",
        )

        # Test Scene 1 has only actor 1 in it
        test_scene_1 = Scene.objects.create(
            scene_author=normal_user_1, scene_name="test_scene", is_active=True
        )
        # Test Scene 2 has both actor 1 and actor 2 in it
        test_scene_2 = Scene.objects.create(
            scene_author=normal_user_2, scene_name="test_scene_2"
        )
        performer_1 = Performer.objects.create(
            parent_user=normal_user_1, discord_snowflake="1234567890210"
        )
        performer_2 = Performer.objects.create(
            parent_user=normal_user_2, discord_snowflake="1234567890211"
        )
        performer_3 = Performer.objects.create(
            parent_user=normal_user_1, discord_snowflake="1234567890212"
        )

        Outfit.objects.create(performer=performer_1, scene=test_scene_1)
        Outfit.objects.create(performer=performer_2, scene=test_scene_2)
        Outfit.objects.create(performer=performer_3, scene=test_scene_1)

    # Test that a user can be properly created as superuser.
    def test_user_properties(self):
        normal = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        self.assertEqual(normal.is_superuser, False)

        superuser = DiscordPointingUser.objects.get(discord_snowflake="1234567899999")
        self.assertEqual(superuser.is_superuser, True)

    # Test that if the user has a primary scene set, that it can access it.
    def test_user_primary_scene(self):
        normal = DiscordPointingUser.objects.get(discord_snowflake="1234567890")
        test_scene = Scene.objects.get(scene_name="test_scene")
        self.assertEqual(normal.active_scene, test_scene)

    # # Test that if the user has no primary scene set, that it can access the first scene it is in.
    # def test_user_no_primary_scene(self):
    #     normal = DiscordPointingUser.objects.get(discord_snowflake="1234567891")
    #     test_scene = Scene.objects.get(scene_name="test_scene_2")
    #     self.assertEqual(normal.active_scene, test_scene)
