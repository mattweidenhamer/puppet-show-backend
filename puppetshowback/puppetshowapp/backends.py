from django.contrib.auth.backends import BaseBackend
from .models import DiscordPointingUser, DiscordData
from .secrets.constants import (
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET,
    API_ENDPOINT,
    DISCORD_AUTH_TOKEN_URL,
    DISCORD_USERS_REDIRECT,
)
import requests


class DiscordAuthBackend(BaseBackend):
    def authenticate(self, request):
        code = request.GET.get("code")
        data = {
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": DISCORD_USERS_REDIRECT,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            token_exchange_response = requests.post(
                DISCORD_AUTH_TOKEN_URL, data=data, headers=headers, timeout=4
            )
            token_exchange_response.raise_for_status()
        except Exception as e:
            return None
        token_data = token_exchange_response.json()
        access_token = token_data["access_token"]
        try:
            response = requests.get(
                f"{API_ENDPOINT}/users/@me",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=4,
            )
            response.raise_for_status()
            user_data = response.json()
        except (requests.exceptions.RequestException, ValueError, KeyError):
            return None
        discord_id = user_data["id"]
        try:
            user = DiscordPointingUser.objects.get(
                discord_data__user_snowflake=discord_id
            )
        except DiscordPointingUser.DoesNotExist:
            try:
                discord_data_obj = DiscordData.objects.get(user_snowflake=discord_id)
            except DiscordData.DoesNotExist:
                discord_data_obj = DiscordData.objects.create(
                    user_snowflake=discord_id,
                    user_username=user_data["username"],
                    user_discriminator=user_data["discriminator"],
                )
            user = DiscordPointingUser.objects.create(discord_data=discord_data_obj)
        return user

    def get_user(self, user_id):
        try:
            return DiscordPointingUser.objects.get(pk=user_id)
        except DiscordPointingUser.DoesNotExist:
            return None
