from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.text import gettext_lazy as _

from gonk.models import Task
from gonk.registry import REGISTRY


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id',
            'started_on',
            'finished_on',
            'revert_started_on',
            'revert_finished_on',
            'status',
        )


class RetrieveTaskSerializer(TaskSerializer):
    class Meta:
        model = Task
        fields = TaskSerializer.Meta.fields + (
            'log',
            'results',
        )


class CreateTaskSerializer(serializers.Serializer):
    task_type = serializers.CharField(max_length=255)
    task_input = serializers.JSONField(default={})
    queue = serializers.CharField(max_length=32, default='celery')
    eta = serializers.DateTimeField(default=timezone.now)
    retryable = serializers.BooleanField(default=False)
    max_retries = serializers.IntegerField(default=0)
    retry_seconds = serializers.IntegerField(default=0)

    def validate_task_type(self, value):
        if value not in REGISTRY.registry.keys():
            raise ValidationError(_('No task found for this type'))

        return value

    class Meta:
        fields = ('task_type', 'input', 'queue')
