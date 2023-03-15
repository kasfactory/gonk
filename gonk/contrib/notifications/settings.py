from django.conf import settings


MERCURE_HUB_URL = getattr(settings, 'MERCURE_HUB_URL', '')
MERCURE_JWT_KEY = getattr(settings, 'MERCURE_JWT_KEY', '')

DEFAULT_NOTIFICATION_EMAIL = getattr(settings, 'DEFAULT_NOTIFICATION_EMAIL', '')
