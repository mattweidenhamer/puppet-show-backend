from django.core.management.base import BaseCommand, CommandError
from puppetshowapp.models import Performer


# TODO delete before live
class Command(BaseCommand):
    help = "View all scenes"

    def handle(self, *args, **options):
        accounts = Performer.objects.all()
        for obj in accounts:
            print(obj)
            print(obj.discord_avatar)
            print(obj.discord_username)
            print(obj.discord_snowflake)
            print(obj.parent_user)
            print(obj.settings)
            print(obj.identifier)
