from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from gonk.contrib.rest_framework.exceptions import APIValidationException
from gonk.exceptions import TaskRunnerValidationException
from gonk.models import Task
from gonk.contrib.rest_framework import permissions
from gonk.contrib.rest_framework import serializers


class TaskViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = serializers.TaskSerializer
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()

        return super().get_queryset().filter(username=self.request.user.username)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateTaskSerializer
        if self.action == 'retrieve':
            return serializers.RetrieveTaskSerializer

        return self.serializer_class

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), permissions.CanCreateTaskPermission()]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer = self.serializer_class(instance=task)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        try:
            validated_data = serializer.validated_data
            user = self.request.user
            params = {'username': user.username, **validated_data}
            return Task.create_task(**params)
        except TaskRunnerValidationException as e:
            raise APIValidationException(str(e))

    @action(methods=['put', 'patch'], detail=True, permission_classes=[
        IsAuthenticated,
        permissions.CanRevertTaskPermission
    ])
    def revert(self, request, *args, **kwargs) -> Response:
        task = self.get_object()
        task.revert()
        serializer = self.get_serializer_class()
        serializer = serializer(instance=task)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[
        IsAuthenticated,
        permissions.CanCancelTaskPermission
    ])
    def cancel(self, request, pk, *args, **kwargs) -> Response:
        task = self.get_object()
        task.cancel()
        serializer = self.get_serializer_class()
        serializer = serializer(instance=task)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
