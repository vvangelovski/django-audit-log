class FieldRegistry(object):
    _registry = {}
    
    def __init__(self, fieldcls):
        self._fieldcls = fieldcls

    
    def add_field(self, model, field):
        reg = self.__class__._registry.setdefault(self._fieldcls, {}).setdefault(model, [])
        reg.append(field)
    
    def get_fields(self, model):
        return self.__class__._registry.setdefault(self._fieldcls, {}).get(model, [])
    
    def __contains__(self, model):
        return model in self.__class__._registry.setdefault(self._fieldcls, {})

