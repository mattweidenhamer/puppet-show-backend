from django.db import models
from enum import Enum
import uuid
import os
from .configuration_models import Outfit
from django.utils import timezone


def user_pfp_path(instance, filename):
    return f"profiles/{instance.user_username}/{filename}"


def user_outfit_path(instance, filename):
    return f"actors/{filename}"


# The user's snowflake, Discord Name, and any other neccesary parts
# OLD DATA, should not be needed again
# class  DiscordData(models.Model):
#     user_snowflake = models.CharField(max_length=20)
#     user_username = models.CharField(max_length=100)
#     user_discriminator = models.CharField(max_length=4)

#     # TODO if we every start capturing profile pictures
#     # To obtain: Get query cdn.discordapp.com/avatars/{user_snowflake}/user_avatar.png
#     profile_picture = models.ImageField(upload_to=user_pfp_path)

#     def __str__(self) -> str:
#         return str(self.user_username)

#     class Meta:
#         db_table = "discord_user_data"


# An outfit's animation
class Animation(models.Model):
    class Attributes(models.TextChoices):
        START_SPEAKING = "START_SPEAKING"
        STOP_SPEAKING = "NOT_SPEAKING"
        SLEEPING = "SLEEPING"
        CONNECTION = "CONNECTION"
        DISCONNECT = "DISCONNECTION"

    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE)
    animation_type = models.CharField(max_length=30, choices=Attributes.choices)
    animation_path = models.URLField(max_length=200)

    @property
    def get_owner(self):
        return self.outfit.get_owner

    def __str__(self) -> str:
        return str(f"{self.outfit}" + f"{self.animation_type}")

    class Meta:
        db_table = "animations"


def default_log_location(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"logs/{now:%Y%m%d%H%M%S}{milliseconds}{extension}"


# A file for handling and mapping the storage of logs.
class LogFile(models.Model):
    class LogType(models.TextChoices):
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"

    log_type = models.CharField(max_length=30, choices=LogType.choices)
    log_file = models.FileField(upload_to=default_log_location)

    def __str__(self) -> str:
        return str(f"{self.log_type}" + f"{self.log_file}")

    class Meta:
        db_table = "log_files"
