import importlib
from datetime import datetime, timedelta
from typing import Type, Optional

from django.db import models
from django.utils import timezone
from django.utils.text import gettext_lazy as _

from gonk.registry import REGISTRY
from gonk.settings import TaskStatusChoices
from gonk.taskrunners import TaskRunner


class Task(models.Model):
    celery_id = models.CharField(max_length=120)
    runner_path = models.CharField(max_length=255)
    input = models.JSONField(default=dict)

    results = models.JSONField(default=dict)
    username = models.CharField('Username', max_length=100, default='')
    started_on = models.DateTimeField(null=True, blank=True)
    finished_on = models.DateTimeField(null=True, blank=True)
    revert_started_on = models.DateTimeField(null=True, blank=True)
    revert_finished_on = models.DateTimeField(null=True, blank=True)

    log = models.TextField(default='')
    status = models.CharField(max_length=5,
                              choices=TaskStatusChoices.choices,
                              default=TaskStatusChoices.PENDING)
    expire_on = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    queue = models.CharField(max_length=32, default='celery')

    retryable = models.BooleanField(default=False)
    retry_time = models.DurationField(default=timedelta(seconds=0), null=True, blank=True)
    retries = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    class Meta:
        permissions = (
            ('can_create_task', _('Can create task')),
            ('can_revert_task', _('Can revert task')),
            ('can_cancel_task', _('Can cancel task')),
        )

    @classmethod
    def create_task(
            cls,
            task_type,
            task_input,
            username='',
            eta: Optional[datetime] = None,
            queue='celery',
            retryable: bool = False,
            retry_seconds: int = 0,
            max_retries: int = 0
    ):
        runner_path = REGISTRY.registry.get(task_type)

        retry_time = timedelta(seconds=retry_seconds)

        task = cls(
            runner_path=runner_path,
            input=task_input,
            queue=queue,
            username=username,
            retryable=retryable,
            retry_time=retry_time,
            max_retries=max_retries,
        )

        expiration = task.get_taskrunner().expiration
        task.expire_on = timezone.now() + expiration if expiration else None
        task.run(eta=eta)
        return task

    @classmethod
    def cleanup(cls):
        for t in Task.objects.filter(expire_on__lte=timezone.now()):
            t.expire()
            t.delete()

    def get_taskrunner_class(self) -> Type[TaskRunner]:
        class_module, class_name = self.runner_path.rsplit('.', 1)
        module = importlib.import_module(class_module)
        return getattr(module, class_name)

    def get_taskrunner(self) -> TaskRunner:
        taskrunner = self.get_taskrunner_class()
        return taskrunner(self)

    def validate(self) -> bool:
        return self.get_taskrunner().validate()

    def run(self, eta: Optional[datetime] = None):
        from gonk.tasks import to_run

        self.validate()

        if not self.id:
            self.save()

        celery_task = to_run.apply_async(queue=self.queue, kwargs={'task_id': self.id}, eta=eta)
        self.celery_id = celery_task.id

        self.save(update_fields=['celery_id'])

    def retry(self):
        if not self.retryable:
            return

        if self.retries > self.max_retries:
            self.get_taskrunner().notify(_('Max retries exceeded'))
            return

        from gonk.tasks import to_retry

        when = timezone.now() + self.retry_time
        celery_task = to_retry.apply_async(queue=self.queue, kwargs={'task_id': self.id}, eta=when)
        self.celery_id = celery_task.id

        self.save(update_fields=['celery_id'])

    def cancel(self, terminate=False):
        from celery.result import AsyncResult

        AsyncResult(self.celery_id).revoke(terminate=terminate)
        self.status = TaskStatusChoices.CANCELED

        self.save()

    def revert(self):
        from gonk.tasks import to_revert

        celery_task = to_revert.delay(task_id=self.id)
        self.celery_id = celery_task.id

        self.save(update_fields=['celery_id'])

    def expire(self):
        self.get_taskrunner().expire()

    def log_status(self, record, checkpoint: bool = False):
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        if checkpoint:
            new_line = '{:20} {:70}  Status: {:>15}\n'.format(now, record, self.status)
        else:
            new_line = '{:20} {:70}\n'.format(now, record)

        self.log += new_line

        if checkpoint:
            self.save()
            self.get_taskrunner().notify(data=record)
