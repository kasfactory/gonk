import argparse
import datetime
import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from gonk.models import Task


class Command(BaseCommand):
    """
        Usage:

        python manage.py create_task <task_type> --raw-input='{}'
        cat file.json | python manage.py create_task <task_type> --queue="celery" --input -
    """
    def add_arguments(self, parser):
        parser.add_argument(
            'task_type',
            type=str,
            help=f'Task type identifier'
        )
        parser.add_argument(
            '--input',
            type=argparse.FileType('r'),
            required=False,
            help='File input -- can be redirected from standard output'
        )
        parser.add_argument(
            '--raw-input',
            type=str,
            required=False,
            help='Raw string input -- Must be in json format'
        )
        parser.add_argument(
            '--queue',
            type=str,
            required=False,
            default='celery',
            help='Celery queue name in which the task will be run'
        )
        parser.add_argument(
            '--when',
            type=str,
            required=False,
            help='Scheduled task run date -- ISO Format'
        )

    def handle(self, task_type, input, raw_input, queue, when, *args, **options):
        data = None
        eta = timezone.now()

        if input:
            data = json.loads(input.read())

        if raw_input:
            data = json.loads(raw_input)

        if when:
            eta = datetime.datetime.fromisoformat(when)

        Task.create_task(
            task_type=task_type,
            task_input=data,
            queue=queue,
            eta=eta,
        )

        self.stdout.write(self.style.SUCCESS(f'Created task to run on {eta}'))
