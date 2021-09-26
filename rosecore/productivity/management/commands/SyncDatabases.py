from django.core.management.base import BaseCommand, CommandError
from .services import ProjectService

class SyncProjectDatabase(BaseCommand):
    help = 'This will sync the project Databases'

    def handle(self, *args, **kwargs):
        try:
            ProjectService.sync()
        except:
            raise CommandError('Initalization failed.')
