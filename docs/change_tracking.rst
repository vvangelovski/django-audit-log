Tracking Users Who Interacted With a Model
=============================================

Tracking who created a model instance
----------------------------------------

You can track user information when model instances get created. For example::

    from audit_log.models.fields import CreatingUserField, CreatingSessionKeyField

    class ProductCategory(models.Model):
        created_by = CreatingUserField()
        created_session_key = CreatingSessionKeyField()
        name = models.CharField(max_length=15)

This is useful for tracking owners of model objects within your app.


Tracking who made changes to a model
----------------------------------------

Two model fields are provided that in conjunction with the ``audit_log.middleware.UserLoggingMiddleware``
can automatically track who made the last changes to a model instance. For example::

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


