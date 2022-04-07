from django.db.models import signals
from django.utils.deprecation import MiddlewareMixin
from functools import partial as curry

from audit_log import registration, settings
from audit_log.models import fields
from audit_log.models.managers import AuditLogManager

def _disable_audit_log_managers(instance):
    for attr in dir(instance):
        try:
            if isinstance(getattr(instance, attr), AuditLogManager):
                getattr(instance, attr).disable_tracking()
        except AttributeError:
            pass


def _enable_audit_log_managers(instance):
    for attr in dir(instance):
        try:
            if isinstance(getattr(instance, attr), AuditLogManager):
                getattr(instance, attr).enable_tracking()
        except AttributeError:
            pass


class UserLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if settings.DISABLE_AUDIT_LOG:
            return
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            else:
                user = None
            session = request.session.session_key
            update_pre_save_info = curry(self._update_pre_save_info, user, session)
            update_post_save_info = curry(self._update_post_save_info, user, session)
            signals.pre_save.connect(update_pre_save_info,  dispatch_uid = (self.__class__, request,), weak = False)
            signals.post_save.connect(update_post_save_info,  dispatch_uid = (self.__class__, request,), weak = False)

    def process_response(self, request, response):
        if settings.DISABLE_AUDIT_LOG:
            return
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return response

    def process_exception(self, request, exception):
        if settings.DISABLE_AUDIT_LOG:
            return None
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return None

    def _update_pre_save_info(self, user, session, sender, instance, **kwargs):
        registry = registration.FieldRegistry(fields.LastUserField)
        if sender in registry:
            for field in registry.get_fields(sender):
                setattr(instance, field.name, user)

        registry = registration.FieldRegistry(fields.LastSessionKeyField)
        if sender in registry:
            for field in registry.get_fields(sender):
                setattr(instance, field.name, session)


    def _update_post_save_info(self, user, session, sender, instance, created, **kwargs ):
        if created:
            registry = registration.FieldRegistry(fields.CreatingUserField)
            if sender in registry:
                for field in registry.get_fields(sender):
                    setattr(instance, field.name, user)
                    _disable_audit_log_managers(instance)
                    instance.save()
                    _enable_audit_log_managers(instance)


            registry = registration.FieldRegistry(fields.CreatingSessionKeyField)
            if sender in registry:
                for field in registry.get_fields(sender):
                    setattr(instance, field.name, session)
                    _disable_audit_log_managers(instance)
                    instance.save()
                    _enable_audit_log_managers(instance)





class JWTAuthMiddleware(MiddlewareMixin):
    """
    Convenience middleware for users of django-rest-framework-jwt.
    Fixes issue https://github.com/GetBlimp/django-rest-framework-jwt/issues/45
    """


    def get_user_jwt(self, request):
        from rest_framework.request import Request
        from rest_framework.exceptions import AuthenticationFailed
        from django.utils.functional import SimpleLazyObject
        from django.contrib.auth.middleware import get_user
        from rest_framework_jwt.authentication import JSONWebTokenAuthentication

        user = get_user(request)
        if user.is_authenticated:
            return user
        try:
            user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
            if user_jwt is not None:
                return user_jwt[0]
        except AuthenticationFailed:
            pass
        return user

    def process_request(self, request):
        from django.utils.functional import SimpleLazyObject
        assert hasattr(request, 'session'),\
        """The Django authentication middleware requires session middleware to be installed.
         Edit your MIDDLEWARE setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."""

        request.user = SimpleLazyObject(lambda: self.get_user_jwt(request))
