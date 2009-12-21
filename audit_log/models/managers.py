import copy
import datetime
from django.db import models

from audit_log.models.fields import LastUserField

class LogEntryObjectDescriptor(object):
    def __init__(self, model):
        self.model = model
    
    def __get__(self, instance, owner):
        values = (getattr(instance, f.attname) for f in self.model._meta.fields)
        return self.model(*values)

class AuditLogManager(models.Manager):
    def __init__(self, model, instance = None):
        super(AuditLogManager, self).__init__()
        self.model = model
        self.instance = instance
    
    def get_query_set(self):
        if self.instance is None:
            return super(AuditLogManager, self).get_query_set()
        
        f = {self.instance._meta.pk.name : self.instance.pk}
        return super(AuditLogManager, self).get_query_set().filter(**f)
    
    def most_recent(self):
        """
        Returns the most recent copy of the instance available in the audit log.
        """
        
        if not self.instance:
            raise TypeError("Can't use moset_recent() without a %s instance."%
             self.instance._meta.object_name)
        fields = (field.name for field in self.instance._meta.fields)
        
        try:
            values = self.values_list(*fields)[0]
        
        except IndexError:
            raise self.instance.DoesNotExist("%s has no audit log entries."% self.instance._meta.object_name)
        
        return self.instance.__class__(*values)
    
    def as_of(self, date):
        """
        Returns an instance of the original model with all the attributes set
        according to what was present on the object on the date provided.
        """
        
        if not self.instance:
            raise TypeError("Can't use as_of() without an instance of %s"% self.instance._meta.object_name)
            fields = (field.name for field in self.instance._meta.fields)
            qs = self.filter(action_date__lte = date)
            try:
                values = qs.values_list('history_type', *fields)[0]
            except IndexError:
                raise self.instance.DoesNotExist("%s was not yet created as of %s."%(self.instance._meta.object_name, date))
            
            if values[0] == '-':
                raise self.instance.DoesNotExist("%s has been deleted."%(self.instance._meta.object_name))
            
            return self.instance.__class__(*values[1:])
            
class AuditLogDescriptor(object):
    def __init__(self, model):
        self.model = model
    
    def __get__(self, instance, owner):
        if instance is None:
            return AuditLogManager(self.model)
        return AuditLogManager(self.model, instance)

class AuditLog(object):
    def contribute_to_class(self, cls, name):
        self.manager_name = name
        models.signals.class_prepared.connect(self.finalize, sender = cls)
    
    
    def create_log_entry(self, instance, action_type):
        manager = getattr(instance, self.manager_name)
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)
        manager.create(action_type = action_type, **attrs)
    
    def post_save(self, instance, created, **kwargs):
        self.create_log_entry(instance, created and 'I' or 'U')
    
    
    def post_delete(self, instance, **kwargs):
        self.create_log_entry(instance,  'D')
    
    
    def finalize(self, sender, **kwargs):
        log_entry_model = self.create_log_entry_model(sender)
        
        models.signals.post_save.connect(self.post_save, sender = sender, weak = False)
        models.signals.post_delete.connect(self.post_delete, sender = sender, weak = False)
        
        descriptor = AuditLogDescriptor(log_entry_model)
        setattr(sender, self.manager_name, descriptor)
    
    def copy_fields(self, model):
        """
        Creates copies of the fields for the provided model, returning a 
        dictionary mapping field name to a copied field object.
        """
        fields = {'__module__' : model.__module__}
        
        for field in model._meta.fields:
            field  = copy.copy(field)
            
            if isinstance(field, models.AutoField):
                #we replace the AutoField of the original model
                #with an IntegerField because a model can
                #have only one autofield.
                
                field.__class__ = models.IntegerField
            
            if field.primary_key or field.unique:
                #unique fields of the original model
                #can not be guaranteed to be unique
                #in the audit log entry but they
                #should still be indexed for faster lookups.
                
                field.primary_key = False
                field._unique = False
                field.db_index = True
            
            fields[field.name] = field
            
        return fields
        
    def get_extra_fields(self, model):
        """
        Returns a dictionary mapping of the fields that are used for
        keeping the acutal audit log entries
        """
        rel_name = '_%s_audit_log_entry'%model._meta.object_name.lower()
        
        return {
            'action_id' : models.AutoField(primary_key = True),
            'action_date' : models.DateTimeField(default = datetime.datetime.now),
            'action_user' : LastUserField(related_name = rel_name),
            'action_type' : models.CharField(max_length = 1, choices = (
                ('I', 'Created'),
                ('U', 'Changed'),
                ('D', 'Deleted'),
            )),
            'action_object' : LogEntryObjectDescriptor(model),
            '__unicode__' : lambda self: u'%s as of %s'% (self.action_object, self.action_date),
        }
            
    
    def get_meta_options(self, model):
        """
        Returns a dictionary of fileds that will be added to
        the Meta inner class of the log entry model.
        """
        return {
            'ordering' : ('-action_date',),
        }
    
    def create_log_entry_model(self, model):
        """
        Creates a log entry model that will be associated with
        the model provided.
        """
        
        attrs = self.copy_fields(model)
        attrs.update(self.get_extra_fields(model))
        attrs.update(Meta = type('Meta', (), self.get_meta_options(model)))
        name = '%sAuditLog'%model._meta.object_name
        return type(name, (models.Model,), attrs)
        