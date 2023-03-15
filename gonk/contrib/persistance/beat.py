import json

try:
    from django_celery_beat.models import CrontabSchedule, PeriodicTask
except ImportError as e:
    raise ImportError(
        'Required dependency django_celery_beat is not installed. '
        'Perhaps you want to install persistance extra dependencies. '
    ) from e


def add_persistent_celery_beat(name: str, task: str, schedule: CrontabSchedule, *args):
    PeriodicTask.objects.create(
        name=name,
        task='gonk.tasks.run_schedule',
        crontab=schedule,
        args=json.dumps([task, *args]),
    )
