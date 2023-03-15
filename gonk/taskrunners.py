from typing import Optional

from dateutil.relativedelta import relativedelta


class BaseTaskRunner:
    expiration: Optional[relativedelta] = None
    reversible: bool = True

    def __init__(self, task):
        self.task = task

    def validate(self):
        """
        :raises gonk.exceptions.TaskRunnerValidationException:
        """
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def revert(self):
        raise NotImplementedError()

    def notify(self, data: str):
        raise NotImplementedError()

    def retry(self):
        raise NotImplementedError()


class TaskRunner(BaseTaskRunner):

    def run(self):
        pass

    def revert(self):
        pass

    def notify(self, data: str):
        pass

    def retry(self):
        return self.run()

    def expire(self):
        pass
