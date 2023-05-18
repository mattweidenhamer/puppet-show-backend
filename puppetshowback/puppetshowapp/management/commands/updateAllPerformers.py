from django.core.management.base import BaseCommand, CommandError
from puppetshowapp.models import Performer


class Command(BaseCommand):
    help = "Update all performers"

    def handle(self, *args, **options):
        performers = Performer.objects.all()
        count = 0
        for performer in performers:
            performer.request_update_user_info()
            count += 1
        print(f"Updated {count} performers")
