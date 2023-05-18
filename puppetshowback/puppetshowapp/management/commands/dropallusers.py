from django.core.management.base import BaseCommand, CommandError
from puppetshowapp.models import DiscordPointingUser


# TODO delete before live
class Command(BaseCommand):
    help = "Drop all users"

    def handle(self, *args, **options):
        accounts = DiscordPointingUser.objects.all()
        count = accounts.count()
        accounts.delete()
        print(f"Deteled {count} accounts")
