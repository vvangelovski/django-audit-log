from django.db import models
from django.conf import settings

from audit_log import registration


class LastUserField(models.ForeignKey):
    """
    A field that keeps the last user that saved an instance
    of a model. None will be the value for AnonymousUser.
    """
    
    def __init__(self, to = getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), null = True, editable = False,  **kwargs):
        super(LastUserField, self).__init__(to = to, null = null, editable = editable, **kwargs)
    
    def contribute_to_class(self, cls, name):
        super(LastUserField, self).contribute_to_class(cls, name)
        registry = registration.FieldRegistry(self.__class__)
        registry.add_field(cls, self)

class LastSessionKeyField(models.CharField):
    """
    A field that keeps a reference to the last session key that was used to access the model.
    """
    
    def __init__(self, max_length  = 40, null = True, editable = False,  **kwargs):
        super(LastSessionKeyField, self).__init__(max_length = 40, null = null, editable = editable, **kwargs)
    
    def contribute_to_class(self, cls, name):
        super(LastSessionKeyField, self).contribute_to_class(cls, name)
        registry = registration.FieldRegistry(self.__class__)
        registry.add_field(cls, self)

class CreatingUserField(LastUserField):
    """
    A field that keeps track of the user that created a model instance.
    This will only be set once upon an INSERT in the database.
    """
    #dont actually need to do anything, everything is handled by the parent class
    #the different logic goes in the middleware
    pass

class CreatingSessionKeyField(LastSessionKeyField):
    """
    A field that keeps track of the last session key with which a model instance was created.
    This will only be set once upon an INSERT in the database.
    """
    #dont actually need to do anything, everything is handled by the parent class
    #the different logic goes in the middleware
    pass


#South stuff:

rules = [((LastUserField, CreatingUserField),
    [],    
    {   
        'to': ['rel.to', {'default': getattr(settings, 'AUTH_USER_MODEL', 'auth.User')}],
        'null': ['null', {'default': True}],
    },)]

try:
    from south.modelsinspector import add_introspection_rules
    # Add the rules for the `LastUserField`
    add_introspection_rules(rules, ['^audit_log\.models\.fields\.LastUserField'])
    add_introspection_rules(rules, ['^audit_log\.models\.fields\.CreatingUserField'])
    add_introspection_rules([], ['^audit_log\.models\.fields\.LastSessionKeyField'])
    add_introspection_rules([], ['^audit_log\.models\.fields\.CreatingSessionKeyField'])
except ImportError:
    pass