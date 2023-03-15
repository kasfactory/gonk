from gonk.beat import add_beat_to_celery


class TaskRegistry:
    def __init__(self):
        self.registry = {}

    def register(self, name, taskrunner):
        self.registry[name] = f"{taskrunner.__module__}.{taskrunner.__qualname__}"

    def register_beat(self, name, taskrunner, cron):
        self.registry[name] = f"{taskrunner.__module__}.{taskrunner.__qualname__}"

        add_beat_to_celery(name, 'gonk.tasks.run_schedule', cron, [name])


REGISTRY = TaskRegistry()
