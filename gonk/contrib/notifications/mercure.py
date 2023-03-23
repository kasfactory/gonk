from threading import Thread

import jwt
import requests
from gonk.contrib.notifications import settings


def make_request(headers, data):
    return requests.post(
        settings.MERCURE_HUB_URL,
        data=data,
        headers=headers,
    )


def publish_event(topic: str, targets: list, data: str) -> 'requests.Response':
    """
    Publishes an event to the Mercury Hub.
    topic: The topic the event will be sent to. Only subscribers who request this topic will get notified.
    targets: The targets that are eligible to get the event.
    data: The data to publish
    """
    token = get_jwt_token([], targets)
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'topic': topic,
        'data': data,
        'private': 'on'
    }

    return requests.post(
        settings.MERCURE_HUB_URL,
        data=data,
        headers=headers,
    )


def get_jwt_token(subscribe_targets: list, publish_targets: list) -> str:
    """
    Creates a Mercure JWT token with the subscribe and publish targets.
    The JWT token gets signed with a key shared with the Mercure Hub.
    """
    return jwt.encode(
        {
            'mercure': {
                'subscribe': subscribe_targets,
                'publish': publish_targets
            }
        },
        settings.MERCURE_JWT_KEY,
        algorithm='HS256'
    ).decode('utf-8')


class MercureNotificationMixin:
    def get_username(self):
        return self.task.username if self.task.username else settings.DEFAULT_NOTIFICATION_EMAIL

    def get_topic_name(self):
        username = self.get_username()
        return f'gonk-event-{username}-{self.task.celery_id}'

    def notify(self, data):
        if settings.MERCURE_HUB_URL:
            username = self.get_username()
            topic = self.get_topic_name()

            t = Thread(target=publish_event, args=(topic, [topic, username], data))
            t.start()

        super(MercureNotificationMixin, self).notify(data)
