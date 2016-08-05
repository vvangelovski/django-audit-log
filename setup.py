import os, sys
from setuptools import setup, find_packages

import audit_log
from audit_log import VERSION, __version__

if VERSION[-1] == 'final':
    STATUS = ['Development Status :: 5 - Production/Stable']
elif 'beta' in VERSION[-1]:
    STATUS = ['Development Status :: 4 - Beta']
else:
    STATUS = ['Development Status :: 3 - Alpha']

def get_readme():
    try:
        return  open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
    except IOError:
        return ''

setup(
    name = 'django-audit-log',
    version = __version__,
    packages = find_packages(exclude = ['testproject']),
    author = 'Vasil Vangelovski',
    author_email = 'vvangelovski@gmail.com',
    license = 'New BSD License (http://www.opensource.org/licenses/bsd-license.php)',
    description = 'Audit trail for django models',
    long_description = get_readme(),
    url = 'https://github.com/Atomidata/django-audit-log',
    download_url = 'https://github.com/Atomidata/django-audit-log/downloads',
    include_package_data = True,
    zip_safe = False,

    classifiers = STATUS + [
       'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
         'Programming Language :: Python',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7',
         'Programming Language :: Python :: 3',
         'Programming Language :: Python :: 3.2',
         'Programming Language :: Python :: 3.3',
         'Programming Language :: Python :: 3.4',
    ],
)
