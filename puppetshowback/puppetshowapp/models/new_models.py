from django.db import models
from .authentication_models import DiscordPointingUser
import uuid
from ..secrets.constants import API_ENDPOINT
from django.dispatch import receiver
from django.db.models.signals import pre_init
import requests
from ..secrets.constants import DISCORD_BOT_TOKEN
from ..constants import DEFAULT_PERFORMER_SETTINGS


# This model is created by DPUs are are bound to them.
# It contains an identifier, a discord snowflake, and a discord username.
# When the identifier is called in the URL, access the parent user's default scene and load this user's corresponding actor.
class Performer(models.Model):
    identifier = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    parent_user = models.ForeignKey(DiscordPointingUser, on_delete=models.CASCADE)
    discord_snowflake = models.CharField(max_length=25)
    discord_username = models.CharField(max_length=30)
    discord_avatar = models.URLField(max_length=200)
    settings = models.JSONField(default=DEFAULT_PERFORMER_SETTINGS)

    @property
    def get_outfit(self):
        if self.parent_user.active_scene is None:
            return None
        return self.parent_user.active_scene.outfits.filter(performer=self).first()

    @property
    def get_owner(self):
        return self.parent_user

    def request_update_user_info(self, save=True):
        url = API_ENDPOINT + f"/users/{self.discord_snowflake}"
        headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
        response = requests.get(
            url,
            headers=headers,
        )
        if response.status_code == 200:
            response_json = response.json()
            self.discord_username = response_json["username"]
            self.discord_avatar = f"cdn.discordapp.com/avatars/{self.discord_snowflake}/{response_json['avatar']}.png"
            if save:
                self.save()
        else:
            print(f"Failed to update user info for {self.discord_username}")
            print(f"Response code: {response.status_code}")
            print(f"Response json: {response.json()}")
