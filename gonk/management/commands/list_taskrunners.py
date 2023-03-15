from django.core.management.base import BaseCommand
from gonk.registry import REGISTRY


class Command(BaseCommand):
    def handle(self, *args, **options):
        available_taskrunners = REGISTRY.registry.keys()

        self.stdout.write(self.style.SUCCESS('Available taskrunners: '))

        for taskrunner in available_taskrunners:
            self.stdout.write(f'- {taskrunner}')
