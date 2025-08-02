=====================
django-honeypot-admin
=====================

.. image:: https://travis-ci.org/Alien501/django-admin-honeypot.svg?branch=develop
   :target: https://travis-ci.org/Alien501/django-admin-honeypot
   :alt: Travis-CI

.. image:: https://coveralls.io/repos/Alien501/django-admin-honeypot/badge.svg?branch=develop
   :target: https://coveralls.io/r/Alien501/django-admin-honeypot
   :alt: Coverage

.. image:: https://codeclimate.com/github/Alien501/django-admin-honeypot/badges/gpa.svg?branch=develop
   :target: https://codeclimate.com/github/Alien501/django-admin-honeypot
   :alt: Code Climate


**django-honeypot-admin** is a fake Django admin login screen to log and notify
admins of attempted unauthorized access. This app was inspired by discussion
in and around Paul McMillan's security talk at DjangoCon 2011.

* **Original Author**: `Derek Payton <http://dmpayton.com/>`_
* **Current Maintainer**: `Vignesh (Alien501) <https://github.com/Alien501/>`_
* **Version**: 2.0.0
* **License**: MIT
* **Django Compatibility**: 3.2+ (Latest Django versions supported)

Documentation
=============

http://django-honeypot-admin.readthedocs.io

tl;dr
-----

* Install django-honeypot-admin from PyPI::

        pip install django-honeypot-admin

* Add ``admin_honeypot`` to ``INSTALLED_APPS``
* Update your urls.py:

    ::

        urlpatterns = [
            ...
            path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
            path('secret/', admin.site.urls),
        ]

* Run ``python manage.py migrate``

NOTE: replace ``secret`` in the url above with your own secret url prefix
