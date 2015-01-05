.PHONY: rm-db syncdb-example syncdb-example-custom-auth run-example run-example-custom-auth test

rm-db:
	if [ -a db.sqlite3 ] ; \
	then \
     		rm db.sqlite3 ; \
	fi;

syncdb-example: rm-db

	DJANGO_SETTINGS_MODULE=testproject.settings \
		django-admin.py syncdb

syncdb-example-custom-auth: rm-db

	DJANGO_SETTINGS_MODULE=testproject.settings_custom_auth \
		django-admin.py syncdb


run-example:
	python testproject/manage.py runserver --settings=testproject.settings

run-example-custom-auth:
	python testproject/manage.py runserver --settings=testproject.settings_custom_auth

test:
	python testproject/manage.py test --settings=testproject.settings
	python testproject/manage.py test --settings=testproject.settings_custom_auth
