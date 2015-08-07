from __future__ import unicode_literals

import copy
import datetime
from django.db import models
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from audit_log.models.fields import LastUserField
from audit_log import settings as local_settings


try:
    from django.utils.timezone import now as datetime_now
    assert datetime_now
except ImportError:
    import datetime
    datetime_now = datetime.datetime.now


class LogEntryObjectDescriptor(object):
    def __init__(self, model):
        self.model = model


    def __get__(self, instance, owner):
        kwargs = dict((f.attname, getattr(instance, f.attname))
                    for f in self.model._meta.fields
                    if hasattr(instance, f.attname))
        return self.model(**kwargs)


class AuditLogManager(models.Manager):
    def __init__(self, model, attname, instance = None, ):
        super(AuditLogManager, self).__init__()
        self.model = model
        self.instance = instance
        self.attname = attname
        #set a hidden attribute on the  instance to control wether we should track changes
        if instance is not None and not hasattr(instance, '__is_%s_enabled'%attname):
            setattr(instance, '__is_%s_enabled'%attname, True)



    def enable_tracking(self):
        if self.instance is None:
            raise ValueError("Tracking can only be enabled or disabled "
                                    "per model instance, not on a model class")
        setattr(self.instance, '__is_%s_enabled'%self.attname, True)

    def disable_tracking(self):
        if self.instance is None:
            raise ValueError("Tracking can only be enabled or disabled "
                                    "per model instance, not on a model class")
        setattr(self.instance, '__is_%s_enabled'%self.attname, False)

    def is_tracking_enabled(self):
        if local_settings.DISABLE_AUDIT_LOG:
            return False
        if self.instance is None:
            raise ValueError("Tracking can only be enabled or disabled "
                                    "per model instance, not on a model class")
        return getattr(self.instance, '__is_%s_enabled'%self.attname)

    def get_queryset(self):
        if self.instance is None:
            return super(AuditLogManager, self).get_queryset()

        f = {self.instance._meta.pk.name : self.instance.pk}
        return super(AuditLogManager, self).get_queryset().filter(**f)


class AuditLogDescriptor(object):
    def __init__(self, model, manager_class, attname):
        self.model = model
        self.manager_class = manager_class
        self.attname = attname

    def __get__(self, instance, owner):
        if instance is None:
            return  self.manager_class(self.model, self.attname)
        return self.manager_class(self.model, self.attname, instance)


class AuditLog(object):

    manager_class = AuditLogManager

    def __init__(self, exclude = []):
        self._exclude = exclude


    def contribute_to_class(self, cls, name):
        self.manager_name = name
        models.signals.class_prepared.connect(self.finalize, sender = cls)


    def create_log_entry(self, instance, action_type):
        manager = getattr(instance, self.manager_name)
        attrs = {}
        for field in instance._meta.fields:
            if field.attname not in self._exclude:
                attrs[field.attname] = getattr(instance, field.attname)
        manager.create(action_type = action_type, **attrs)

    def post_save(self, instance, created, **kwargs):
        #ignore if it is disabled
        if getattr(instance, self.manager_name).is_tracking_enabled():
            self.create_log_entry(instance, created and 'I' or 'U')


    def post_delete(self, instance, **kwargs):
        #ignore if it is disabled
        if getattr(instance, self.manager_name).is_tracking_enabled():
            self.create_log_entry(instance,  'D')


    def finalize(self, sender, **kwargs):
        log_entry_model = self.create_log_entry_model(sender)

        models.signals.post_save.connect(self.post_save, sender = sender, weak = False)
        models.signals.post_delete.connect(self.post_delete, sender = sender, weak = False)

        descriptor = AuditLogDescriptor(log_entry_model, self.manager_class, self.manager_name)
        setattr(sender, self.manager_name, descriptor)

    def copy_fields(self, model):
        """
        Creates copies of the fields we are keeping
        track of for the provided model, returning a
        dictionary mapping field name to a copied field object.
        """
        fields = {'__module__' : model.__module__}

        for field in model._meta.fields:

            if not field.name in self._exclude:

                field  = copy.deepcopy(field)

                if isinstance(field, models.AutoField):
                    #we replace the AutoField of the original model
                    #with an IntegerField because a model can
                    #have only one autofield.

                    field.__class__ = models.IntegerField

                if field.primary_key:
                    field.serialize = True

                #OneToOne fields should really be tracked
                #as ForeignKey fields
                if isinstance(field, models.OneToOneField):
                    field.__class__ = models.ForeignKey


                if field.primary_key or field.unique:
                    #unique fields of the original model
                    #can not be guaranteed to be unique
                    #in the audit log entry but they
                    #should still be indexed for faster lookups.

                    field.primary_key = False
                    field._unique = False
                    field.db_index = True


                if field.rel and field.rel.related_name:
                    field.rel.related_name = '_auditlog_%s' % field.rel.related_name                
                elif field.rel: 
                    try:
                        if field.rel.get_accessor_name():
                            field.rel.related_name = '_auditlog_%s' % field.rel.get_accessor_name()
                    except:
                        pass
  
                fields[field.name] = field

        return fields



    def get_logging_fields(self, model):
        """
        Returns a dictionary mapping of the fields that are used for
        keeping the acutal audit log entries.
        """
        rel_name = '_%s_audit_log_entry'%model._meta.object_name.lower()


        def entry_instance_to_unicode(log_entry):
            try:
                result = '%s: %s %s at %s'%(model._meta.object_name,
                                                log_entry.object_state,
                                                log_entry.get_action_type_display().lower(),
                                                log_entry.action_date,

                                                )
            except AttributeError:
                result = '%s %s at %s'%(model._meta.object_name,
                                                log_entry.get_action_type_display().lower(),
                                                log_entry.action_date

                                                )
            return result

        action_user_field = LastUserField(related_name = rel_name, editable = False)

        #check if the manager has been attached to auth user model
        if [model._meta.app_label, model.__name__] == getattr(settings, 'AUTH_USER_MODEL', 'auth.User').split("."):
            action_user_field = LastUserField(related_name = rel_name, editable = False, to = 'self')

        return {
            'action_id' : models.AutoField(primary_key = True),
            'action_date' : models.DateTimeField(default = datetime_now, editable = False, blank=False),
            'action_user' : action_user_field,
            'action_type' : models.CharField(max_length = 1, editable = False, choices = (
                ('I', _('Created')),
                ('U', _('Changed')),
                ('D', _('Deleted')),
            )),
            'object_state' : LogEntryObjectDescriptor(model),
            '__unicode__' : entry_instance_to_unicode,
        }


    def get_meta_options(self, model):
        """
        Returns a dictionary of Meta options for the
        autdit log model.
        """
        result = {
            'ordering' : ('-action_date',),
            'app_label' : model._meta.app_label,
        }
        from django.db.models.options import DEFAULT_NAMES
        if 'default_permissions' in DEFAULT_NAMES:
            result.update({'default_permissions': ()})
        return result

    def create_log_entry_model(self, model):
        """
        Creates a log entry model that will be associated with
        the model provided.
        """

        attrs = self.copy_fields(model)
        attrs.update(self.get_logging_fields(model))
        attrs.update(Meta = type(str('Meta'), (), self.get_meta_options(model)))
        name = str('%sAuditLogEntry'%model._meta.object_name)
        return type(name, (models.Model,), attrs)
