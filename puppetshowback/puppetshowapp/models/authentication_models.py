from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
import logging
import requests
from ..secrets.constants import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET
from rest_framework.authtoken.models import Token


class DiscordPointingUserManager(BaseUserManager):
    def create_user(self, *args, **kwargs):
        user = self.model(*args, **kwargs)
        user.save()
        return user

    def create_superuser(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        user.is_superuser = True
        user.save()
        return user


class DiscordPointingUser(AbstractBaseUser):
    # TODO add components and function neccesary for token refreshing
    login_username = models.CharField(max_length=25, unique=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discord_snowflake = models.CharField(max_length=25, unique=True)
    discord_username = models.CharField(max_length=30)

    # discord_data = models.OneToOneField(
    #     DiscordData, on_delete=models.DO_NOTHING, related_name="user_discord_data"
    # )

    is_superuser = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    # added_users = models.ManyToManyField(
    #     DiscordData, blank=True, related_name="added_users"
    # )

    discord_auth_token = models.CharField(max_length=100)
    discord_refresh_token = models.CharField(max_length=100)
    discord_avatar = models.CharField(max_length=100)

    objects = DiscordPointingUserManager()
    USERNAME_FIELD = "login_username"
    REQUIRED_FIELDS = ["discord_snowflake"]

    # def __str__(self) -> str:
    #     if self.discord_data.user_username is None:
    #         return self.user_id
    #     return self.discord_data.user_username

    def get_owner(self):
        return self

    def has_perm(self, perm, obj=None):
        from .configuration_models import Outfit, Scene
        from .new_models import Performer

        if self.is_superuser:
            return True
        elif isinstance(obj, Outfit):
            if obj.scene.scene_author.pk == self.pk:
                return True
            return False
        elif isinstance(obj, Scene):
            if obj.scene_author.pk == self.pk:
                return True
            return False
        elif isinstance(obj, DiscordPointingUser):
            if obj.pk == self.pk:
                return True
        elif isinstance(obj, Performer):
            if (obj.parent_user.pk == self.pk) or (
                obj.scene.scene_author.pk == self.pk
            ):
                return True
            return False
        return False

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def scenes(self):
        from .configuration_models import Scene

        return Scene.objects.filter(scene_author=self)

    @property
    def active_scene(self):
        from .configuration_models import Scene

        sceneToReturn = Scene.objects.filter(scene_author=self, is_active=True).first()
        # if sceneToReturn is None:
        #     firstScene = Scene.objects.filter(scene_author=self).first()
        #     if firstScene is not None:
        #         firstScene.is_active = True
        #         firstScene.save()
        #         return firstScene
        return sceneToReturn

    @property
    def added_performers(self):
        from .new_models import Performer

        return Performer.objects.filter(parent_user=self)

    @property
    def added_performers_count(self):
        from .new_models import Performer

        return Performer.objects.filter(parent_user=self).count()

    def refresh_token(self):
        API_ENDPOINT = "https://discord.com/api/v10/oauth2/token"
        data = {
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": self.discord_refresh_token,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post(url=API_ENDPOINT, data=data, headers=headers)
        try:
            r.raise_for_status()
            response = r.json()
            self.discord_auth_token = response["access_token"]
            self.discord_refresh_token = response["refresh_token"]
            self.save()
        except requests.exceptions.HTTPError as e:
            logging.error(f"Error refreshing token for user {self.login_username}")
            logging.error(e)
            logging.error("Response text: " + r.text)
            logging.error("Revoking token for user" + self.discord_username)
            Token.objects.delete(user=self)

    def make_user_get_request(self, url):
        if self.discord_auth_token is None:
            self.refresh_token()
        headers = {
            "Authorization": f"Bearer {self.discord_auth_token}",
        }
        print(headers)
        r = requests.get(
            url=url,
            headers=headers,
            timeout=4,
        )
        return r

    def save(self, *args, **kwargs):
        if not self.login_username:
            self.login_username = f"{self.discord_snowflake}"
        super().save(*args, **kwargs)
