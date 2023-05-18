from django.core.management.base import BaseCommand, CommandError
from puppetshowapp.models import DiscordPointingUser, DiscordData
from getpass import getpass


class Command(BaseCommand):
    help = "Creates a normal user with a Discord-Pointing Account."

    def add_arguments(self, parser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        email = input("Email: ")
        while True:
            discord_id = input("Discord Data snowflake: ")
            if DiscordData.objects.filter(user_snowflake=discord_id).exists():
                break
            self.stdout.write(self.style.ERROR("No match found with that snowflake."))
        while True:
            password1 = getpass()
            password2 = getpass("Password (again): ")
            if password1 == password2:
                break
            self.stdout.write(self.style.ERROR("Passwords don't match."))

        user = DiscordPointingUser.objects.create_user_from_snowflake(
            email=email, password=password1, discord_snowflake=discord_id
        )
        self.stdout.write(self.style.SUCCESS("Superuser created."))
