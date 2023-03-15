from gonk.registry import REGISTRY
from celery.schedules import crontab


def register(name):
    def register_class(cls):
        REGISTRY.register(name, cls)
        return cls

    return register_class


def register_beat(name, cron: crontab):
    def register_class(cls):
        REGISTRY.register_beat(name, cls, cron)
        return cls

    return register_class
