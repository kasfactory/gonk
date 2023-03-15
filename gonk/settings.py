# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


STATUS_ERROR = 'ERROR'
STATUS_PENDING = 'PENDI'
STATUS_DOING = 'DOING'
STATUS_DONE = 'DONE'
STATUS_CANCELLING = 'CANCG'
STATUS_CANCELED = 'CANCD'
STATUS_TO_REVERT = 'TOREV'
STATUS_REVERTING = 'REVTG'
STATUS_REVERTED = 'REVTD'
STATUS_RETRYING = 'RTRNG'
STATUS_RETRY_ERROR = 'RTERR'


class TaskStatusChoices(models.TextChoices):
    ERROR = STATUS_ERROR, _('Error')
    PENDING = STATUS_PENDING, _('To DO')
    DOING = STATUS_DOING, _('Doing')
    DONE = STATUS_DONE, _('Done')
    CANCELLING = STATUS_CANCELLING, _('Cancelling')
    CANCELED = STATUS_CANCELED, _('Canceled')
    TO_REVERT = STATUS_TO_REVERT, _('To Revert')
    REVERTING = STATUS_REVERTING, _('Reverting')
    REVERTED = STATUS_REVERTED, _('Reverted')
    RETRYING = STATUS_RETRYING, _('Retrying')
    RETRY_ERROR = STATUS_RETRY_ERROR, _('Retry error')


OK = u'OK'
KO = u'KO'
WARNING = u'WA'
TASK_RESULT = (
    (OK, u'OK'),
    (KO, u'ERROR'),
    (WARNING, u'WARNING'),
)
