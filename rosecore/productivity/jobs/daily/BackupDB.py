from django_extensions.management.jobs import BaseJob
from django.conf import settings
from django.core import management
import time
import os

class Job(BaseJob):
    help = "Backup database job, should run daily"

    def execute(self):
        # To load backup:./manage.py loaddata json_file
        filename = f'db_backup_{time.strftime("%Y%m%d-%H%M%S")}.json'
        management.call_command('dumpdata', '>', os.path.join(settings.BACKUP_DIR, filename))
