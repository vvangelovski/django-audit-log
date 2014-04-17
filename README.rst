============================
django-audit-log
============================

Tracking changes to django models.

* Model fields for keeping track of the user and session that created and modified a model instance.
* A model manager class that can automatically track all the changes made to a model in the database.
* Support for Django 1.6, South migrations and custom User classes.

`The documentation can be found here <https://readthedocs.org/projects/django-audit-log/>`_ 

**Tracking full model history on M2M relations Is not supported yet.**
**Version 0.3.0 onwards is tested with Django 1.6. It should work with older versions of Django, but may break things unexpectedly!**

*Note: This project was not maintained actively for a while. One of the reasons was that I wasn't receiving email notifications from GitHub. The other reason: We were using it just on a couple of projects that were frozen to old versions of Django. If you need any help with the project you can contact me by email directly if I don't respond to your GitHub issues. Feel free to nudge me over email if you have a patch for something. You can find my email in the AUTHORS file.*