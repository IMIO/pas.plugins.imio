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

.. image:: https://travis-ci.org/IMIO/pas.plugins.imio.png
    :target: http://travis-ci.org/IMIO/pas.plugins.imio

.. image:: https://coveralls.io/repos/github/IMIO/pas.plugins.imio/badge.svg?branch=master
    :target: https://coveralls.io/github/IMIO/pas.plugins.imio?branch=master

Instalation
-----------

Install pas.plugins.imio from addons page.

To update list of users, go to one of this view : 

- /@@add-authentic-users?type=usagers
- /@@add-authentic-users?type=agents


Translations
------------

This product has been translated into

- English
- French


Installation
------------
You need libffi-dev package installed (`sudo apt install libffi-dev`)
Install pas.plugins.imio by adding it to your buildout::

    [buildout]

    ...

    eggs =
        pas.plugins.imio


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/IMIO/pas.plugins.imio/issues
- Source Code: https://github.com/IMIO/pas.plugins.imio


Support
-------

If you are having issues, please let us know.
We have a mailing list located at: devs@imio.be


License
-------

The project is licensed under the GPLv2.
