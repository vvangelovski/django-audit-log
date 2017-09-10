
Tracking full model history
===============================

In order to enable historic tracking on a model, the model needs to have a
property of type ``audit_log.models.managers.AuditLog`` attached::


    from django.db import models
    from audit_log.models.fields import LastUserField
    from audit_log.models.managers import AuditLog


    class ProductCategory(models.Model):
        name = models.CharField(max_length=150, primary_key = True)
        description = models.TextField()

        audit_log = AuditLog()

    class Product(models.Model):
        name = models.CharField(max_length = 150)
        description = models.TextField()
        price = models.DecimalField(max_digits = 10, decimal_places = 2)
        category = models.ForeignKey(ProductCategory)

        audit_log = AuditLog()


Each time you add an instance of AuditLog to any of your models you need to run
``python manage.py syncdb`` so that the database table that keeps the actual
audit log for the given model gets created.


Querying the audit log
-------------------------------

An instance of ``audit_log.models.managers.AuditLog`` will behave much like a
standard manager in your model. Assuming the above model
configuration you can go ahead and create/edit/delete instances of Product,
to query all the changes that were made to the products table
you would need to retrieve all the entries for the audit log for that
particular model class::

    In [2]: Product.audit_log.all()
    Out[2]: [<ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:29.292363>,
            <ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:24.898991>,
            <ProductAuditLogEntry: Product: My Gadget super changed at 2011-02-25 06:04:15.448934>,
            <ProductAuditLogEntry: Product: My Gadget changed at 2011-02-25 06:04:06.566589>,
            <ProductAuditLogEntry: Product: My Gadget created at 2011-02-25 06:03:57.751222>,
            <ProductAuditLogEntry: Product: My widget created at 2011-02-25 06:03:42.027220>]

Accordingly you can get the changes made to a particular model instance like so::

    In [4]: Product.objects.all()[0].audit_log.all()
    Out[4]: [<ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:29.292363>,
            <ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:24.898991>,
            <ProductAuditLogEntry: Product: My widget created at 2011-02-25 06:03:42.027220>]

Instances of ``AuditLog`` behave like django model managers and can be queried in the same fashion.

The querysets yielded by ``AuditLog`` managers are querysets for models
of type ``[X]AuditLogEntry``, where X is the tracked model class.
An instance of ``XAuditLogEntry`` represents a log entry for a particular model
instance and will have the following fields that are of relevance:

    * ``action_id`` - Primary key for the log entry.
    * ``action_date`` - The point in time when the logged action was performed.
    * ``action_user`` - The user that performed the logged action.
    * ``action_type`` - The type of the action (Created/Changed/Deleted)
    * Any field of the original ``X`` model that is tracked by the audit log.


M2M Relations
--------------------

Tracking changes on M2M Relations doesn't work for now. If you really need to track changes on M2M relations with
this package, explicitly define the table with another model instead of declaring the M2M relation.

Abstract Base Models
--------------------------

For now just attaching the ``AuditLog`` manager to an abstract base model won't make it automagically attach itself on the child
models. Just attach it to every child separately.

Disabling/Enabling Tracking on a Model Instance
-------------------------------------------------
There may be times when you want a certain ``save()`` or ``delete()`` on a model instance to be ignored by the audit log.
To disable tracking on a model instance you simply call::

    modelinstance.audit_log.disable_tracking()

To re-enable it do::

    modelinstance.audit_log.enable_tracking()

Note that this only works on instances, trying to do that on a model class will raise an exception.

Using in combination with ``django-modeltranslation``
----------------------------------------------

``django-modeltranslation`` is a package that allows you to add dynamic translation of model fields (`documentation`_). Behind the scenes ``django-modeltranslation`` automatically modifies your models by adding translation fields. To keep your tracking models created by ``django-audit-log`` matching your tracked models,  you have to remember to register the tracking models for translation as well as your tracked models. Here's an example:

.. code:: python

    from modeltranslation.translator import register, TranslationOptions

    from my_app import models


    @register(models.MyModel)
    @register(models.MyModel.audit_log.model)
    class MyModelTranslationOptions(TranslationOptions):
        """Translation options for MyModel."""

        fields = (
            'text',
            'title',
        )

If you forget to register your tracking models, you will get an error like:

.. code::

    TypeError: 'text_es' is an invalid keyword argument for this function

.. _documentation: https://django-modeltranslation.readthedocs.io/en/latest/
