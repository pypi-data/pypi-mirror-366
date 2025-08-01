===========
EPIC Sample
===========

This package is a companion to the django-epic package.  Its purpose
is to provide a minimal but functional environment that let's a
potential user of EPIC get a feel for how the application works.

Install this package with::

	pip install django-epic-sample

After installation, start the Django test server with::

	python -m epic_sample.manage runserver

Then point your web-browser at::

	http://localhost:8000/epic/

This page should prompt you to log in.  You can use::

	- username = admin
	- password = admin

for this sample site.

To run the EPIC unit tests, use::

	python -m epic_sample.manage test epic.tests
