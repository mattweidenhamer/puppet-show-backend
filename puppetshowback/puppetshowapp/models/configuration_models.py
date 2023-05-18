from django.db import models
from .authentication_models import DiscordPointingUser
from .new_models import Performer
from enum import Enum
from uuid import uuid4
import os
from ..constants import DEFAULT_OUTFIT_SETTINGS, DEFAULT_SCENE_SETTINGS


def user_outfit_path(instance, filename):
    return f"profiles/{instance.user_snowflake}/{filename}"


# A "scene" is a configuration of the specific information of displayed users.
# The active scene dictates how loaded users will be displayed.
class Scene(models.Model):
    identifier = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    scene_name = models.CharField(max_length=30)
    scene_author = models.ForeignKey(DiscordPointingUser, on_delete=models.CASCADE)
    scene_settings = models.JSONField(default=DEFAULT_SCENE_SETTINGS)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.scene_name} scene"

    class Meta:
        db_table = "scenes"

    @property
    def outfits(self):
        return Outfit.objects.filter(scene=self)

    @property
    def get_owner(self):
        return self.scene_author

    def set_active(self):
        for scene in Scene.objects.filter(scene_author=self.scene_author):
            scene.is_active = False
            scene.save()
        self.is_active = True
        self.save()

    @property
    def preview_image(self):
        if self.outfits.count() == 0:
            return None
        return self.outfits.first().getFirstImage()


# An "Outfit" is a configuration of a performer's appearance.
# It is bound to a scene and a performer.
class Outfit(models.Model):
    # The identifier
    identifier = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    # The user actually being drawn
    performer = models.ForeignKey(Performer, on_delete=models.CASCADE)

    # The scene the outfit is in
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)

    # A display name for the outfit
    outfit_name = models.CharField(max_length=30)

    # Any additional settings
    settings = models.JSONField(default=DEFAULT_OUTFIT_SETTINGS)

    @property
    def animations(self):
        from .data_models import Animation

        return Animation.objects.filter(outfit=self)

    def getImage(self, attribute):
        for animation in self.animations.all():
            if animation.animation_type == attribute:
                return animation.animation_path
        return None

    def getFirstImage(self):
        for animation in self.animations.all():
            return animation.animation_path
        return None

    @property
    def get_owner(self):
        return self.scene.scene_author

    class Meta:
        db_table = "charactor_actors"

    def __str__(self) -> str:
        return f"{self.performer.discord_username}'s {self.scene.scene_name} outfit"

    def save(self, *args, **kwargs):
        if self.outfit_name is None or self.outfit_name == "":
            self.outfit_name = self.performer.discord_username
        super().save(*args, **kwargs)

    # def setImage(self, attribute, image):
    #     def _deleteImage(image):
    #         try:
    #             if os.path.isfile(image.path):
    #                 os.remove(image.path)
    #         except ValueError:
    #             pass

    #     # If there's already an animation for it in the file, overwrite it.
    #     for animation in self.animations.all():
    #         if animation.animation_type == attribute:
    #             _deleteImage(animation.animation_image)
    #             animation.animation_image = image
    #             animation.save()
    #             return

    #     # Otherwise, create a new one and add it.
    #     self.animations.create(animation_type=attribute, animation_image=image)
    #     self.save()


# An "emotion" is an extra configuration of states.
# Eventually, a user from another portion of the site should be able to push a button
# that changes their emotion on the website.

# NYI


# class Emotion(models.Model):
#     # A unique hash of the person's ID, the emotion name,
#     emotion_hash = models.CharField(max_length=200)

#     # The emotion "name," default to "Neutral"
#     emotion_name = models.CharField(max_length=15, default="Neutral")

#     # What actor they belong to
#     actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

#     # Default animations
#     speaking_animation = models.ImageField(upload_to=user_actor_path)
#     not_speaking_animation = models.ImageField(upload_to=user_actor_path)

#     # When not speaking for a while, NYI
#     sleeping_animation = models.ImageField(upload_to=user_actor_path)

#     # NYI
#     connection_animation = models.ImageField(upload_to=user_actor_path)
#     disconnect_animation = models.ImageField(upload_to=user_actor_path)

#     class Meta:
#         db_table = "character_emotions"
