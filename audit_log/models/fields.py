from django.db import models
from django.contrib.auth.models import User
from audit_log import registration

class LastUserField(models.ForeignKey):
    """
    A field that keeps the last user that saved an instance
    of a model. None will be the value for AnonymousUser.
    """
    
    def __init__(self, to = User, null = True,  **kwargs):
        super(LastUserField, self).__init__(to = to, null = null, **kwargs)
    
    def contribute_to_class(self, cls, name):
        super(LastUserField, self).contribute_to_class(cls, name)
        registry = registration.FieldRegistry(self.__class__)
        registry.add_field(cls, self)

class LastSessionKeyField(models.CharField):
    """
    A field that keeps a reference to the last session key that was used to access the model.
    """
    
    def __init__(self, max_length  = 40, null = True,  **kwargs):
        super(LastSessionKeyField, self).__init__(max_length = 40, null = null, **kwargs)
    
    def contribute_to_class(self, cls, name):
        super(LastSessionKeyField, self).contribute_to_class(cls, name)
        registry = registration.FieldRegistry(self.__class__)
        registry.add_field(cls, self)