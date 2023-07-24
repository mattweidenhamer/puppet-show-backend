from django.test import TestCase
from puppetshowapp.models.authentication_models import DiscordPointingUser
from puppetshowapp.models.configuration_models import Scene, Outfit
from puppetshowapp.models.new_models import Performer


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
