========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
        | |codeclimate| |codeclimate-tests|
    * - package
      - | |version| |wheel|
        | |supported-versions| |supported-implementations|
    * - docs
      - |docs|

.. |docs| image:: http://octokitpy.readthedocs.io/en/latest/?badge=latest
    :target: https://readthedocs.org/projects/octokitpy
    :alt: Documentation Status

.. |codeclimate| image:: https://codeclimate.com/github/khornberg/octokit.py/badges/gpa.svg
   :target: https://codeclimate.com/github/khornberg/octokit.py
   :alt: CodeClimate Quality Status

.. |codeclimate-tests| image:: https://api.codeclimate.com/v1/badges/7954d60682bc6d6c15cd/test_coverage
   :target: https://codeclimate.com/github/khornberg/octokit.py
   :alt: Test Coverage

.. |version| image:: https://img.shields.io/pypi/v/octokitpy.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/octokitpy/

.. |wheel| image:: https://img.shields.io/pypi/wheel/octokitpy.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/octokitpy/

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/octokitpy.svg
    :alt: Supported versions
    :target: https://pypi.org/project/octokitpy/

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/octokitpy.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/octokitpy/


.. end-badges

Python client for GitHub API


Installation
============

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
    repos = Octokit().repos.list_for_user(username="octokit")
    for repo in repos.json:
        print(repo["name"])
    # Make an unauthenticated request for octokit's public repositories

Webhooks::

    from octokit import webhook
    webhook.verify(headers, payload, secret, events=['push'])

:code:`octokit.py` provides a function to verify `webhooks <https://developer.github.com/webhooks/>`_ sent to your application.

    headers
        dictionary of request headers

    payload
        string; payload of request

    secret
        string; secret provided to GitHub to sign webhook

    events
        list; events that you want to receive

    verify_user_agent
        boolean; whether or not you want to verify the user agent string of the request

    return_app_id
        boolean; whether or not you want to return the app id from the ping event for GitHub applications. This will only return the ``id`` if the event is the ``ping`` event. Otherwise the return value will be boolean.


Note that webhook names are available at :code:`from octokit_routes import webhook_names`

Authentication
--------------

Instantiate a client with the authentication scheme and credentials that you want to use.

basic::

    octokit = Octokit(auth='basic', username='myuser', password='mypassword')

token::

    response = Octokit(auth='token', token='yak').authorization.get(id=100)

app::

    octokit = Octokit(auth='app', app_id='42', private_key=private_key)

app installation::

    octokit = Octokit(auth='installation', app_id='42', private_key=private_key)

For applications, provide the application id either from the ping webhook or the application's page on GitHub.
The :code:`private_key` is a string of your private key provided for the application.
The :code:`app` scheme will use the application id and private key to get a token for the first installation id of the application.

API Schema/Routes/Specifications
--------------------------------

One can instantiate the ``Octokit`` with ``routes=specification`` where the ``specification`` is one of ``api.github.com``, ``ghe-2.15``, etc.

Data
----

The :code:`octokit` client based on the available `route data <https://github.com/khornberg/octokitpy-routes>`_ and `webhook data <https://github.com/khornberg/octokitpy-routes>`_

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




Tests
-----

::

    [x] unit tests

    [ ] integration tests - need fixtures to assert against

    [x] coverage uploaded to code climate

Errors
------

::

    [ ] Raise `OctokitValidationError` for param validation error

    [ ] Raise `OctokitAuthenticationError` for auth error

    [ ] Raise `OctokitRateLimitError` for rate limiting errors

Best Practices
--------------

::

    [ ] throttling

    [ ] handles rate limiting

    [x] pagination

Generated Documentation
-----------------------

::

    [ ] Auto generated documentation

Deployment
----------

::

    [x] Deploy wheels

    [ ] GitHub releases


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
