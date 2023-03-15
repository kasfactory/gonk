from celery import _state as state
from celery.schedules import crontab


def add_beat_to_celery(name: str, task: str, cron: crontab, args):
    state.current_app.conf.beat_schedule.update({
        name: {
            'task': task,
            'schedule': cron,
            'args': args
        }
    })
