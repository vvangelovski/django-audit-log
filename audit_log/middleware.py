from audit_log import registration, settings
from audit_log.models import fields
from audit_log.models.managers import AuditLogManager
from django.db.models import signals
from django.utils.functional import curry, cached_property


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


def _register_post_save_field(field_cls, sender, instance, obj):
    registry = registration.FieldRegistry(field_cls)
    if sender in registry:
        for field in registry.get_fields(sender):
            setattr(instance, field.name, obj)
            _disable_audit_log_managers(instance)
            instance.save()
            _enable_audit_log_managers(instance)


def _register_pre_save_field(field_cls, sender, instance, obj):
    registry = registration.FieldRegistry(field_cls)
    if sender in registry:
        for field in registry.get_fields(sender):
            setattr(instance, field.name, obj)


class UserLoggingMiddleware(object):
    def process_request(self, request):
        if settings.DISABLE_AUDIT_LOG:
            return
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            props = {
                'user': request.user if hasattr(request, 'user') and request.user.is_authenticated() else None,
                'userprofile': request.userprofile if hasattr(request, 'userprofile') else None,
                'session': request.session.session_key,
            }

            update_pre_save_info = curry(self._update_pre_save_info, **props)
            update_post_save_info = curry(self._update_post_save_info, **props)
            signals.pre_save.connect(update_pre_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.post_save.connect(update_post_save_info, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        if settings.DISABLE_AUDIT_LOG:
            return
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def process_exception(self, request, exception):
        if settings.DISABLE_AUDIT_LOG:
            return None
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        return None

    def _update_pre_save_info(self, sender, instance, **kwargs):
        _register_pre_save_field(field_cls=fields.LastUserField, sender=sender, instance=instance, obj=kwargs['user'])
        _register_pre_save_field(field_cls=fields.LastSessionKeyField, sender=sender, instance=instance,
                                 obj=kwargs['session'])
        _register_pre_save_field(field_cls=fields.UserProfileField, sender=sender, instance=instance,
                                 obj=kwargs['userprofile'])

    def _update_post_save_info(self, sender, instance, created, **kwargs):
        if created:
            _register_post_save_field(field_cls=fields.CreatingUserField, sender=sender, instance=instance,
                                      obj=kwargs['user'])
            _register_post_save_field(field_cls=fields.CreatingSessionKeyField, sender=sender, instance=instance,
                                      obj=kwargs['session'])
            _register_post_save_field(field_cls=fields.UserProfileField, sender=sender, instance=instance,
                                      obj=kwargs['userprofile'])


class APIAuthMiddleware(object):
    """
    Middleware to lazy load APIAuth object in case if one is different from default django object.
    """

    @cached_property
    def auth_class(self):
        module, clazz = settings.API_AUTH_CLASS.rsplit('.', 1)
        import importlib
        module = importlib.import_module(module)
        return getattr(module, clazz)

    def get_user(self, request):
        from rest_framework.request import Request
        from rest_framework.exceptions import AuthenticationFailed

        try:
            user, _ = self.auth_class().authenticate(Request(request))
            if user is not None:
                return user
        except AuthenticationFailed:
            pass
        return None

    def process_request(self, request):
        from django.utils.functional import SimpleLazyObject
        from django.contrib.auth.middleware import get_user

        user = get_user(request)

        if not user.is_authenticated():
            request.userprofile = SimpleLazyObject(lambda: self.get_user(request))
        else:
            request.userprofile = None
