from django.core.management.base import BaseCommand, CommandError
from puppetshowapp.models import Scene


# TODO delete before live
class Command(BaseCommand):
    help = "View all scenes"

    def handle(self, *args, **options):
        accounts = Scene.objects.all()
        for obj in accounts:
            print(obj)
            print(obj.is_active)
