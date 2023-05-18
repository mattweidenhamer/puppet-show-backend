from django.core.management.base import BaseCommand
from puppetshowapp.models import DiscordPointingUser
import requests
from ...secrets.constants import API_ENDPOINT


class Command(BaseCommand):
    help = "Update all Discord tokens."
    # TODO may not be required anymore

    def handle(self, *args, **options):
        count = 0
        for user in DiscordPointingUser.objects.all():
            user.refresh_token()
            try:
                response = requests.get(
                    f"{API_ENDPOINT}/users/@me",
                    headers={"Authorization": f"Bearer {user.discord_auth_token}"},
                    timeout=4,
                )
                response.raise_for_status()
                user_data = response.json()
            except (requests.exceptions.RequestException, ValueError, KeyError) as e:
                return e
            user.discord_avatar = user_data["avatar"]
            user.discord_username = user_data["username"]
            user.save()
            count += 1
        print(f"Updated {count} Discord users")
