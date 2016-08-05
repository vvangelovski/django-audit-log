from django.conf import settings as global_settings

DISABLE_AUDIT_LOG = getattr(global_settings, 'DISABLE_AUDIT_LOG', False)
API_AUTH_CLASS = getattr(global_settings, 'AUDIT_LOG_API_AUTH_CLASS', None)
