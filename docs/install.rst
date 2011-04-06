
Installation
===================

Install from PyPI with ``easy_install`` or ``pip``::

    pip install django-audit-log

to hack on the code you can symlink the package in your site-packages from the source tree::

    python setup.py develop


The package audit_log doesn't need to be in your ``INSTALLED_APPS``. The only thing you need
to modify in your ``settings.py`` is add ``audit_log.middleware.UserLoggingMiddleware`` to
the ``MIDDLEWARE_CLASSES`` tupple::

    
    MIDDLEWARE_CLASSES = (
         'django.middleware.common.CommonMiddleware',
         'django.contrib.sessions.middleware.SessionMiddleware',
         'django.contrib.auth.middleware.AuthenticationMiddleware',
         'audit_log.middleware.UserLoggingMiddleware',
    )



