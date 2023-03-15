import json
from datetime import timedelta
from time import sleep

from django.utils import timezone
from gonk.models import Task
from rest_framework import status
from rest_framework.test import APITestCase

from gonk.settings import STATUS_CANCELED
from test_app.tests.mixins import CreateUserMixin


class TestCreateTask(APITestCase, CreateUserMixin):
    def setUp(self) -> None:
        self.username = 'kenobi@starwars.com'
        self.password = 'ihavethehighground'
        self.user = self.create_user(self.username, self.password)

    def test_create_task_not_authenticated(self):
        # List user tasks
        response = self.client.get(f'/tasks/')
        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            }
        }

        # Create task
        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_task_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        # List user tasks
        response = self.client.get(f'/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            }
        }

        # Create task
        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_task(self):
        self.client.force_authenticate(user=self.user)

        # List user tasks
        response = self.client.get(f'/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

        self.add_permission(self.user, 'can_create_task')
        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            }
        }

        # Create task
        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

        # Retrieve task
        task_id = response.data.get('id')
        response = self.client.get(f'/tasks/{task_id}/')
        assert response.status_code == status.HTTP_200_OK

        # List user tasks
        response = self.client.get(f'/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_task_serializer_validation_error(self):
        self.add_permission(self.user, 'can_create_task')
        self.client.force_authenticate(user=self.user)
        data = {
            'task_type': 'not_existing_task_type',
            'task_input': {},
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_task_with_taskrunner_validation_error(self):
        self.add_permission(self.user, 'can_create_task')
        self.client.force_authenticate(user=self.user)
        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 1,
                'element2': -1,
            },
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_schedule_future_task(self):
        self.add_permission(self.user, 'can_create_task')
        self.client.force_authenticate(user=self.user)

        # List user tasks
        response = self.client.get(f'/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            },
            'eta': (timezone.now() + timedelta(days=7)).isoformat(),
        }

        # Create task
        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_cancel_task(self):
        self.add_permission(self.user, 'can_create_task')
        self.add_permission(self.user, 'can_cancel_task')
        self.client.force_authenticate(user=self.user)

        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            }
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

        task_id = response.data.get('id')
        response = self.client.post(f'/tasks/{task_id}/cancel/', content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('status') == STATUS_CANCELED

    def test_create_cancel_task_no_cancel_permission(self):
        self.add_permission(self.user, 'can_create_task')
        self.client.force_authenticate(user=self.user)

        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            }
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

        task_id = response.data.get('id')
        response = self.client.post(f'/tasks/{task_id}/cancel/', content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_revert_task(self):
        self.add_permission(self.user, 'can_create_task')
        self.add_permission(self.user, 'can_revert_task')
        self.client.force_authenticate(user=self.user)

        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            }
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

        task_id = response.data.get('id')
        response = self.client.put(f'/tasks/{task_id}/revert/', content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

    def test_create_cancel_task_no_revert_permission(self):
        self.add_permission(self.user, 'can_create_task')
        self.client.force_authenticate(user=self.user)

        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            }
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

        task_id = response.data.get('id')
        response = self.client.put(f'/tasks/{task_id}/revert/', content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_revert_no_reversible_task(self):
        self.add_permission(self.user, 'can_create_task')
        self.add_permission(self.user, 'can_revert_task')
        self.client.force_authenticate(user=self.user)

        data = {
            'task_type': 'no_reversible',
            'task_input': {}
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

        task_id = response.data.get('id')
        response = self.client.put(f'/tasks/{task_id}/revert/', content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_retryable_task(self):
        self.add_permission(self.user, 'can_create_task')
        self.add_permission(self.user, 'can_revert_task')
        self.client.force_authenticate(user=self.user)

        data = {
            'task_type': 'add',
            'task_input': {
                'element1': 0,
                'element2': 3,
            },
            'retryable': True,
            'max_retries': 5,
            'retry_seconds': 300,
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

        task_id = response.data.get('id')
        task = Task.objects.get(id=task_id)

        assert task.retryable
        assert task.max_retries == 5
        assert task.retry_time.seconds == 300

    def test_create_expirable_task_with_func(self):
        import os
        self.add_permission(self.user, 'can_create_task')
        self.client.force_authenticate(user=self.user)

        data = {
            'task_type': 'expirable_with_func',
            'task_input': {
                'element1': 0,
                'element2': 3,
            }
        }

        response = self.client.post('/tasks/', data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

        task_id = response.data.get('id')
        sleep(5)
        Task.cleanup()
        self.assertEqual(Task.objects.filter(id=task_id).first(), None)
        self.assertEqual(open('created_on_expire', 'r').read(), 'hello')
        os.remove("created_on_expire")
