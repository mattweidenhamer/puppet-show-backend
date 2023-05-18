from django.core.management.base import BaseCommand, CommandError
from puppetshowapp.models import DiscordPointingUser


class Command(BaseCommand):
    help = "Drop all superusers from the superuser table."

    def handle(self, *args, **options):
        adminaccounts = DiscordPointingUser.objects.filter(is_staff=True)
        count = adminaccounts.count()
        adminaccounts.delete()
        print(f"Deleted {str(count)} users.")
