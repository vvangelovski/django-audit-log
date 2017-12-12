from django.db.models import Model
from django.utils.translation import ugettext_lazy as _
from audit_log.models.fields import CreatingUserField, CreatingSessionKeyField, LastUserField, LastSessionKeyField

class AuthStampedModel(Model):
	"""
	An abstract base class model that provides auth and session information
	fields.
	"""
	created_by = CreatingUserField(verbose_name = _("created by"), related_name = "created_%(app_label)s_%(class)s_set")
	created_with_session_key = CreatingSessionKeyField(_("created with session key"))
	modified_by =  LastUserField(verbose_name = _("modified by"), related_name = "modified_%(app_label)s_%(class)s_set")
	modified_with_session_key = LastSessionKeyField(_("modified with session key"))

	class Meta:
		abstract = True
