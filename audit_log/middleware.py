from django.db.models import signals
from django.utils.functional import curry

from audit_log import registration
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

class UserLoggingMiddleware(object):
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user

            else:
                user = None

            session = request.session.session_key

            update_pre_save_info = curry(self._update_pre_save_info, user, session)
            update_post_save_info = curry(self._update_post_save_info, user, session)
            signals.pre_save.connect(update_pre_save_info,  dispatch_uid = (self.__class__, request,), weak = False)
            signals.post_save.connect(update_post_save_info,  dispatch_uid = (self.__class__, request,), weak = False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return response


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
