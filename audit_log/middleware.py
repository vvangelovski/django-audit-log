from django.db.models import signals
from django.utils.functional import curry

from audit_log import registration
from audit_log.models import fields

class UserLoggingMiddleware(object):
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None
        
            update_users = curry(self.update_users, user)
            signals.pre_save.connect(update_users,  dispatch_uid = (self.__class__, request,), weak = False)
    
    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return response
    
    def update_users(self, user, sender, instance, **kwargs):
        registry = registration.FieldRegistry(fields.LastUserField)
        if sender in registry:
            for field in registry.get_fields(sender):
                setattr(instance, field.name, user)
    
