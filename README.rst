========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |travis| |pyup|
        | |codeclimate| |codeclimate-tests|
    * - package
      - | |version| |wheel|
        | |supported-versions| |supported-implementations|
    * - docs
      - |docs|

.. |docs| image:: http://octokitpy.readthedocs.io/en/latest/?badge=latest
    :target: https://readthedocs.org/projects/octokitpy
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/khornberg/octokit.py.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/khornberg/octokit.py

.. |pyup| image:: https://pyup.io/repos/github/khornberg/octokit.py/shield.svg
     :target: https://pyup.io/repos/github/khornberg/octokit.py/
     :alt: Updates

.. |codeclimate| image:: https://codeclimate.com/github/khornberg/octokit.py/badges/gpa.svg
   :target: https://codeclimate.com/github/khornberg/octokit.py
   :alt: CodeClimate Quality Status

.. |codeclimate-tests| image:: https://api.codeclimate.com/v1/badges/7954d60682bc6d6c15cd/test_coverage
   :target: https://codeclimate.com/github/khornberg/octokit.py
   :alt: Test Coverage

.. |version| image:: https://img.shields.io/pypi/v/octokitpy.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/octokitpy

.. |wheel| image:: https://img.shields.io/pypi/wheel/octokitpy.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/octokitpy

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/octokitpy.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/octokitpy

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/octokitpy.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/octokitpy


.. end-badges

Python client for GitHub API


Installation
============

**requires python 3.6+**

Yes that is opinionated. Python 2 is near the end of the life and this is a new project.

*Note octokit and octokit.py were already taken in the cheese shop*

::

    pip install octokitpy

Documentation
=============

https://octokitpy.readthedocs.io/


Example
-------

REST API::

    from octokit import Octokit

    repos = Octokit().repos.get_for_org(org='octokit', type='public')

Default values::

    TODO Show them

Webhooks::

    from octokit import webhook
    webhook.verify(headers, payload, secret, events=['push'])

Authentication
--------------

Instatiate a client with the authentication scheme and credentials that you want to use.

Example::

    client = Octokit(type='app', token='xyz')
    client.repos.get_for_org(org='octokit', type='private')

basic::

    TODO

oauth::

    TODO

oauth key/secret::

    TODO

token::

    TODO

app::

    TODO


Pagination
----------

::

    TODO


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox

Contributing
============

Pull requests are very welcome!

Please see CONTRIBUTING.md for more information.

Credits
=======

Package based on `cookiecutter-pylibrary <https://github.com/ionelmc/cookiecutter-pylibrary>`_

License
=======

MIT
