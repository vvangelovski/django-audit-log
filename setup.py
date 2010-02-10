import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
setup(
    name = 'django-audit-log',
    version = '0.1',
    packages = ['audit_log', 'audit_log.models'],
    author = 'Vasil Vangelovski',
    author_email = 'vvangelovski@gmail.com',
    license = 'New BSD License (http://www.opensource.org/licenses/bsd-license.php)',
    description = 'Audit trail for django models',
    long_description = 'This app automatically tracks changes made to models over time as well as which user made the changes.',
    url = 'http://code.google.com/p/django-audit-log/',
    download_url = 'http://django-audit-log.googlecode.com/files/django-audit-log.0.1.tar.gz',
    include_package_data = True,
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
