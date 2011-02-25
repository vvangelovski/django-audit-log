============================
django-audit-log
============================

Introduction
============================

What It Does
----------------------------

Lets you keep track of who changed what
model instance in you Django application. Full
model structure is tracked and kept in a separate
table similar in structure to the original model table.

Lest's say a user logs in the admin and adds a Product model instance.
The audit log will track this in a separate table with the exact structure of you
Product table plus a reference to the user, the time of the action and type of action
indicating it was an insert.

Next the user does an update of the same Product instance. The audit log table
will keep the previous entry and another one will be added reflecting the change.

When the user deletes the same model instance the audit log table will have an entry
indicating this with the state of the model before it was deleted.

	

What It Doesn't Do
----------------------------

The audit log bootstraps itself on each POST, PUT or DELETE request. So it
can only track changes to model instances when they are
made via the web interface of your application. Note: issuing a delete in a PUT
request will work without a problem. Saving
model instances through the Django shell for instance won't
reflect anything in the audit log. Neither will  direct INSERT, UPDATE or DELETE
statements, either within a request lifecycle or directly in your database shell.


Installation and Usage
============================

Setup
----------------------------

First you need to download the code and put the audit_log folder somewhere on your *PYTHONPATH*. 
Note that _audit_log_ *doesn't* need to be listed in *INSTALLED_APPS* for your project. You can also
install it with *pip install django-audit-log* or *easy_install django-audit-log* or *python setup.py install* from
the source.
Next you need to add *audit_log.middleware.UserLoggingMiddleware* to *MIDDLEWARE_CLASSES* in *settings.py*. 
The inclusion of this middleware class will allow the extension to track the users associated with each change in the audit trail. 
Now, add an instance of audit_log.models.managers.AuditLog to every model you want to track changes on. For example:

example::

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


If you don't want to track changes on a specific field you can specify it in the *exclude* parameter like so:

example::

		class SaleInvoice(models.Model):
		    date = models.DateTimeField(default = datetime.datetime.now)

		    audit_log = AuditLog(exclude = ['date',])
    
    
		    def __unicode__(self):
		        return str(self.date)


Each time you add an instance of AuditLog to any of your models you need to run *python manage.py syncdb*
so that the database table that keeps the actual audit log for the given model gets created.

Querying the Audit Log
--------------------------

An instance of *audit_log.models.managers.AuditLog* will behave much like a standard manager in your model. 
Asuming the above model configuration you can go ahead and create/edit/delete instances of *Product*, 
to query all the changes that were made to the products table you would need to retreive 
all the entries for the audit log for that particular model class:

example::

		In [2]: Product.audit_log.all()
		Out[2]: [<ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:29.292363>, <ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:24.898991>,
				<ProductAuditLogEntry: Product: My Gadget super changed at 2011-02-25 06:04:15.448934>, <ProductAuditLogEntry: Product: My Gadget changed at 2011-02-25 06:04:06.566589>,
				<ProductAuditLogEntry: Product: My Gadget created at 2011-02-25 06:03:57.751222>, <ProductAuditLogEntry: Product: My widget created at 2011-02-25 06:03:42.027220>]


Accordingly you can find the changes made to a particular model instance like so:

example::


		In [4]: Product.objects.all()[0].audit_log.all()
		Out[4]: [<ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:29.292363>, <ProductAuditLogEntry: Product: My widget changed at 2011-02-25 06:04:24.898991>,
				<ProductAuditLogEntry: Product: My widget created at 2011-02-25 06:03:42.027220>]

Any more complex queries via this manager will work accordingly.

The querysets yielded by this manager are querysets of _XAuditLogEntry_ model classes (X being the tracked model class). An instance of *XAuditLogEntry* represents a log entry for the particular model and will have the following fields that are of relevance:

  * action_id - Primary key for the log entry.
  * action_date - The point in time the action was performed. 
  * action_user - The user which performed the action (None for anonymous users).
  * action_type - Created/Changed/Deleted.
  * [model_field_name] - The state of the actual model field instance **after** the action was performed.

Hacking the Code
============================

It's best to create a symlink to your *site-packages* with *python setup.py develop*.

Tests are all in the *testproject* folder.
