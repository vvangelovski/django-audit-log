============================
django-audit-log
============================

Tracking changes to django models.


* Model fields for keeping track of the user and session that created and modified a model instance.
* Abstract model class with fields ``created_by`` and ``modified_by`` fields.
* A model manager class that can automatically track changes made to a model in the database.
* Support for Django 1.6 and 1.7, South migrations, Django 1.7 migrations and custom User classes.

`The documentation can be found here <http://django-audit-log.readthedocs.org/en/latest/index.html>`_ 

**Tracking full model history on M2M relations Is not supported yet.**
**Version 0.3.0 onwards is tested with Django 1.6. It should work with older versions of Django, but may break things unexpectedly!**


Quickstart Guide
===============================

Install it with pip from PyPi::

    pip install django-audit-log

Add ``audit_log.middleware.UserLoggingMiddleware`` to your ``MIDDLEWARE_CLASSES``::


    MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
    )


To just track who created or edited a model instance just make it inherit from ``AuthStampedModel``::


    from audit_log.models import AuthStampedModel

    class WarehouseEntry(AuthStampedModel):
        product = models.ForeignKey(Product)
        quantity = models.DecimalField(max_digits = 10, decimal_places = 2)


This will add 4 fields to the ``WarehouseEntry`` model:

* ``created_by`` - A foreign key to the user that created the model instance.
* ``created_with_session_key`` - Stores the session key with which the model instance was first created.
* ``modified_by`` - A foreign key to the user that last saved a model instance.
* ``modified_with_session_key`` - Stores the session key with which the model instance was last saved.

If you want to track full model change history you need to attach an ``AuditLog`` manager to the model::

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

You can then query the audit log::

    In [2]: Product.audit_log.all()
    Out[2]: [<ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:29.292363>,
            <ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:24.898991>,
            <ProductAuditLogEntry: Product: My Gadget super changed at 2011-02-25 06:04:15.448934>,
            <ProductAuditLogEntry: Product: My Gadget changed at 2011-02-25 06:04:06.566589>,
            <ProductAuditLogEntry: Product: My Gadget created at 2011-02-25 06:03:57.751222>, 
            <ProductAuditLogEntry: Product: My widget created at 2011-02-25 06:03:42.027220>]

`The documentation can be found here <http://django-audit-log.readthedocs.org/en/latest/index.html>`_ 


*Note: This project was not maintained actively for a while. One of the reasons was that I wasn't receiving email notifications from GitHub. The other reason: We were using it just on a couple of projects that were frozen to old versions of Django. If you need any help with the project you can contact me by email directly if I don't respond to your GitHub issues. Feel free to nudge me over email if you have a patch for something. You can find my email in the AUTHORS file.*
