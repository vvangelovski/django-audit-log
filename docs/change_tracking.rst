Tracking Users that Created/Modified a Model
=============================================

``AuthStampedModel`` is an abstract model base class in the vein of ``TimeStampedModel`` from ``django-extensions``.
It has 4 fields used for tracking the user and the session key with which a model instance was created/modified::


    from audit_log.models import AuthStampedModel

    class WarehouseEntry(AuthStampedModel):
        product = models.ForeignKey(Product)
        quantity = models.DecimalField(max_digits = 10, decimal_places = 2)


This will add 4 fields to the ``WarehouseEntry`` model.:

* ``created_by`` - A foreign key to the user that created the model instance.
* ``created_with_session_key`` - Stores the session key with which the model instance was first created.
* ``modified_by`` - A foreign key to the user that last saved a model instance.
* ``modified_with_session_key`` - Stores the session key with which the model instance was last saved.

The related names for the ``created_by`` and ``modified_by`` fields are ``created_%(class)s_set`` and ``modified_%(class)s_set`` respectively::

    In [3]: admin = User.objects.get(username = 'admin')
    In [4]: admin.created_warehouseentry_set.all()
    Out[4]: [<WarehouseEntry: WarehouseEntry object>, <WarehouseEntry: WarehouseEntry object>]
    In [5]: vasil = User.objects.get(username = 'vasil')
    In [6]: vasil.modified_warehouseentry_set.all()
    Out[6]: [<WarehouseEntry: WarehouseEntry object>]

This was done to keep in line with Django's naming for the ``related_name``. If you want to change that or other things you can
create your own abstract base class with the proviced fields. 


Tracking Who Created a Model
----------------------------------------

You can track user information when model instances get created with the ``CreatingUserField`` and ``CreatingSessionKeyField``. For example::

    from audit_log.models.fields import CreatingUserField, CreatingSessionKeyField

    class ProductCategory(models.Model):
        created_by = CreatingUserField(realted_name = "created_categories")
        created_with_session_key = CreatingSessionKeyField()
        name = models.CharField(max_length=15)

This is useful for tracking owners of model objects within your app.


Tracking Who Made the Last Changes to a Model
-----------------------------------------------
``LastUserField`` and ``LastSessionKeyField`` will store the user and session key with which a model instance was last saved::

    from django.db import models
    from audit_log.models.fields import LastUserField, LastSessionKeyField
    
    class Product(models.Model):
        name = models.CharField(max_length = 150)
        description = models.TextField()
        price = models.DecimalField(max_digits = 10, decimal_places = 2)
        category = models.ForeignKey(ProductCategory)
        
        def __unicode__(self):
            return self.name

    class ProductRating(models.Model):
        user = LastUserField()
        session = LastSessionKeyField()
        product = models.ForeignKey(Product)
        rating = models.PositiveIntegerField()

Anytime someone makes changes to the ``ProductRating`` model through the web interface
the reference to the user that made the change will be stored in the user field and 
the session key will be stored in the session field.


