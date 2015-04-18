from django.conf import settings as global_settings

DISABLE_AUDIT_LOG = getattr(global_settings, 'DISABLE_AUDIT_LOG', False)
