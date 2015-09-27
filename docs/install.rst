
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
         'django.contrib.sessions.middleware.SessionMiddleware',
         'django.middleware.common.CommonMiddleware',
         'django.middleware.csrf.CsrfViewMiddleware',
         'django.contrib.auth.middleware.AuthenticationMiddleware',
         'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
         'django.contrib.messages.middleware.MessageMiddleware',
         'django.middleware.clickjacking.XFrameOptionsMiddleware',
         'audit_log.middleware.JWTAuthMiddleware',
         'audit_log.middleware.UserLoggingMiddleware',
    )


For users of ``django-rest-framework-jwt`` you should also include a special middleware
that fixes a compatibility problem with that library::

    MIDDLEWARE_CLASSES = (
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.middleware.common.CommonMiddleware',
      'django.middleware.csrf.CsrfViewMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',
      'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
      'django.contrib.messages.middleware.MessageMiddleware',
      'django.middleware.clickjacking.XFrameOptionsMiddleware',
      'audit_log.middleware.JWTAuthMiddleware',
      'audit_log.middleware.UserLoggingMiddleware',
    )

Note that in that case ``rest_framework_jwt.authentication.JSONWebTokenAuthentication``
should be at the top of ``DEFAULT_AUTHENTICATION_CLASSES``.
