from django.core.management.base import BaseCommand, CommandError
from puppetshowapp.models import Performer


# TODO delete before live
class Command(BaseCommand):
    help = "Drop all performers"

    def handle(self, *args, **options):
        performers = Performer.objects.all()
        count = performers.count()
        performers.delete()
        print(f"Deleted {count} performer")
