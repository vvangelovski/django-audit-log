from django.utils.decorators import decorator_from_middleware

from audit_log.middleware import UserLoggingMiddleware

log_current_user = decorator_from_middleware(UserLoggingMiddleware)
