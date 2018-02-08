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

https://octokitpy.readthedocs.io/en/latest/


Examples
--------

REST API::

    from octokit import Octokit
    repos = Octokit().repos.get_for_org(org='octokit', type='public')
    # Make an unauthenticated request for the public repositories of the octokit organization

Webhooks::

    from octokit import webhook
    webhook.verify(headers, payload, secret, events=['push'])

:code:`octokit.py` provides a function to verify `webhooks <https://developer.github.com/webhooks/>`_ sent to your application.

    headers
        dictionary of request headers

    payload
        payload of request; will be converted to a string via ``json.dumps`` for signature validation

    secret
        string; secret provided to GitHub to sign webhook

    events
        list; events that you want to receive

    verify_user_agent
        boolean; whether or not you want to verify the user agent string of the request

    return_app_id
        boolean; whether or not you want to return the app id from the ping event for GitHub applications. This will only return the ``id`` if the event is the ``ping`` event. Otherwise the return value will be boolean.

Authentication
--------------

Instatiate a client with the authentication scheme and credentials that you want to use.

basic::

    octokit = Octokit(auth='basic', username='myuser', password='mypassword')
    octokit.repos.get_for_org(org='octokit', type='private')

token::

    response = Octokit(auth='token', token='yak').authorization.get(id=100)

app::

    octokit = Octokit(auth='app', app_id=42, private_key=private_key)

For applications provide the application id either from the ping webhook or the application's page on GitHub.
The :code:`private_key` is a string of your private key provided for the application.
The :code:`app` scheme will use the application id and private key to get a token for the first installation id of the application.

TODOs
===========

GitHub APIs
-----------

::

    [-] REST (see best practices, integration tests, and errors)

    [ ] GraphQL client

    [x] GitHub Apps

    [ ] OAuth Apps

    [x] Webhooks

Data
----

The :code:`octokit` client based on the available `rest data <https://github.com/octokit/rest.js/blob/master/lib/routes.json>`_ and `webhook data <https://github.com/octokit/webhooks.js/blob/master/lib/webhook-names.json>`_

::

    [ ] Periodically, check if ``routes.json`` has changed and if so fetch and open a PR for it to be merged

    [ ] Periodically, check if ``webhook-names.json`` has changed and if so fetch and open a PR for it to be merged

Tests
-----

::

    [x] unit tests

    [ ] integration tests - need fixtures to assert against

    [ ] coverage uploaded to code climate -- not sure why it is not working

Errors
------

::

    [ ] Raise :code:`OctokitValidationError` for param validation error

    [ ] Raise :code:`OctokitAuthenticationError` for auth error

    [ ] Raise :code:`OctokitRateLimitError` for rate limiting errors

Best Practices
--------------

::

    [ ] throttling

    [ ] handles rate limiting

    [ ] pagination


**Check box guide**

::

    [ ] Incomplete

    [-] Partially completed

    [x] Completed

Development
===========

To run the all tests run::

    tox

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
