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

Let's say a user logs in the admin and adds a Product model instance.
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
request will work without a problem (but don't do that). Saving
model instances through the Django shell for instance won't
reflect anything in the audit log. Neither will  direct INSERT, UPDATE or DELETE
statements, either within a request lifecycle or directly in your database shell.

