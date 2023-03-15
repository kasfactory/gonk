from time import sleep

from celery.schedules import crontab
from dateutil.relativedelta import relativedelta

from gonk.decorators import register, register_beat
from gonk.exceptions import TaskRunnerValidationException
from gonk.taskrunners import TaskRunner
from gonk.contrib.notifications.mercure import MercureNotificationMixin


@register('add')
class AddTaskRunner(MercureNotificationMixin, TaskRunner):

    def validate(self):
        data = self.task.input

        if data.get('element1') < 0 or data.get('element2') < 0:
            raise TaskRunnerValidationException('element1 and element2 must be equal or higher than 0')

    def run(self):
        self.task.results['solution'] = self.task.input.get('element1', 0) + self.task.input.get('element2', 0)

    def revert(self):
        del self.task.results['solution']


@register('sleep')
class SleepTaskRunner(MercureNotificationMixin, TaskRunner):

    def validate(self):
        pass

    def run(self):
        self.task.log_status('empezando a dormirse')
        sleep(10)
        self.task.log_status('notificacion de 10 segundos', checkpoint=True)
        sleep(10)
        self.task.log_status('notificacion de 20 segundos', checkpoint=True)


@register_beat('print', crontab(minute='*'))
class PrinterRunner(MercureNotificationMixin, TaskRunner):
    def validate(self):
        pass

    def run(self):
        from datetime import datetime
        self.task.log_status(f'scheduled notification: {datetime.now().isoformat()}', checkpoint=True)


@register('no_reversible')
class NoReversibleTaskRunner(MercureNotificationMixin, TaskRunner):
    reversible = False

    def validate(self):
        pass

    def run(self):
        self.task.results['solution'] = 'done'


@register('expirable_with_func')
class ExpirableWithCleanTaskRunner(TaskRunner):
    expiration = relativedelta(seconds=3)

    def validate(self):
        pass

    def run(self):
        self.task.results['solution'] = 'done'

    def expire(self):
        open('created_on_expire', 'w').write('hello')