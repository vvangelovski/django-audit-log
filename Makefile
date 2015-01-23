.PHONY: test

test:
	python audit_log/tests/runtests.py
	python audit_log/tests/runtests_custom_auth.py
