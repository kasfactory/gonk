import logging
import sys
import traceback

from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone

from gonk.beat import add_beat_to_celery
from gonk.models import Task
from gonk.settings import TaskStatusChoices

logger = logging.getLogger(__name__)


def execute(task_id, func):
    try:
        task = Task.objects.get(pk=task_id)
        task.log_status('TASK FOUND')
    except Exception as e:
        logger.error(str(e))
        return

    try:
        func(task)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        task.status = TaskStatusChoices.ERROR
        task.results = {
            "exception": str(e),
            "line": exc_tb.tb_lineno,
            "traceback": traceback.format_exc()
        }
        task.log_status(f'ERROR: {str(e)}', checkpoint=True)
        logger.error(str(e), exc_info=True)
        task.save()

        # Schedule task for retry if task is retryable
        task.retry()


def runner_func(task):
    task.status = TaskStatusChoices.DOING
    task.started_on = timezone.now()
    task.save()
    task.get_taskrunner().run()
    task.finished_on = timezone.now()
    task.status = TaskStatusChoices.DONE
    task.save()


def reverter_func(task):
    task.status = TaskStatusChoices.REVERTING
    task.revert_started_on = timezone.now()
    task.save()
    task.get_taskrunner().revert()
    task.revert_finished_on = timezone.now()
    task.status = TaskStatusChoices.REVERTED
    task.save()


def retry_func(task):
    task.status = TaskStatusChoices.RETRYING
    task.retries += 1
    task.started_on = timezone.now()
    task.save()
    task.get_taskrunner().retry()
    task.finished_on = timezone.now()
    task.status = TaskStatusChoices.DONE
    task.save()


@shared_task()
def to_run(task_id):
    execute(task_id, runner_func)


@shared_task()
def to_retry(task_id):
    execute(task_id, retry_func)


@shared_task()
def to_revert(task_id):
    execute(task_id, reverter_func)


@shared_task()
def run_schedule(task_type, params: dict = None):
    if params is None:
        params = {}

    Task.create_task(task_type, params)


@shared_task()
def cleanup_gonk_tasks():
    Task.cleanup()


add_beat_to_celery('cleanup_gonk_tasks',
                   'gonk.tasks.cleanup_gonk_tasks',
                   crontab(minute=0, hour=4), [])
