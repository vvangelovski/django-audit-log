from django.db import models
from django.contrib.auth.models import User
from audit_log import registration

if hasattr(settings, 'AUTH_USER_MODEL'):
    AUTH_USER_MODEL = settings.AUTH_USER_MODEL
else:
    from django.contrib.auth.models import User
    AUTH_USER_MODEL = User
    

class LastUserField(models.ForeignKey):
    """
    A field that keeps the last user that saved an instance
    of a model. None will be the value for AnonymousUser.
    """
    
    def __init__(self, to = AUTH_USER_MODEL, null = True,  **kwargs):
        super(LastUserField, self).__init__(to = to, null = null, **kwargs)
    
    def contribute_to_class(self, cls, name):
        super(LastUserField, self).contribute_to_class(cls, name)
        registry = registration.FieldRegistry(self.__class__)
        registry.add_field(cls, self)
        
        
rules = [((LastUserField,),
    [],    
    {   
        'to': ['rel.to', {'default': User}],
        'null': ['null', {'default': True}],
    },)]

try:
    from south.modelsinspector import add_introspection_rules
    # Add the rules for the `LastUserField`
    add_introspection_rules(rules, ['^audit_log\.models\.fields\.LastUserField'])
except ImportError:
    pass
