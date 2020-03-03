.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

================
pas.plugins.imio
================

Install local or remote connector to Imio authentic (SSO).


Features
--------

- Override Plone login page
- Connect with SSO
- Disabled edition of username and e-mail
- 

.. image:: https://travis-ci.org/IMIO/pas.plugins.imio.png
    :target: http://travis-ci.org/IMIO/pas.plugins.imio

.. image:: https://coveralls.io/repos/github/IMIO/pas.plugins.imio/badge.svg?branch=master
    :target: https://coveralls.io/github/IMIO/pas.plugins.imio?branch=master


Installation
------------

You need libffi-dev package installed (`sudo apt install libffi-dev`)
Install pas.plugins.imio by adding it to your buildout::

    [buildout]

    ...

    eggs =
        pas.plugins.imio

And then running ``bin/buildout``

After your instance is up, you can now install pas.plugins.imio from addons page.


Usage
-----

To update list of users, go to one of this view : 

- /@@add-authentic-users?type=usagers
- /@@add-authentic-users?type=agents


To login with an user registred into Plone/Zope instead of pas plugin use this view :

- Plone 4: ${portal_url}/login_form
- Plone 5.2+: ${portal_url}/zope_login


Translations
------------

This product has been translated into

- English
- French


Contribute
----------

- Issue Tracker: https://github.com/IMIO/pas.plugins.imio/issues
- Source Code: https://github.com/IMIO/pas.plugins.imio


License
-------

The project is licensed under the GPLv2.
