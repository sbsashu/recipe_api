"""
Wait for db connection command
"""
import time
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Djando command wait for db"""
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database ...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Data base is unavilable wait for 1 sec')
                time.sleep(1)
        self.stdout.write("Database is avilable...")
