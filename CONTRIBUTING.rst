============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps.

Bug reports
===========

When `reporting a bug <https://github.com/khornberg/octokit.py/issues>`_ please include:

    * Your operating system name and version.
    * Any details about your local setup that might be helpful in troubleshooting.
    * Detailed steps to reproduce the bug.

Documentation improvements
==========================

octokit.py could always use more documentation, whether as part of the
official octokit.py docs or even on the web in blog posts, articles, and such.

Feature requests and feedback
=============================

The best way to send feedback is to file an issue at https://github.com/khornberg/octokit.py/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that code contributions are welcome :)

Development
===========

To set up `octokit.py` for local development:

1. Fork `octokit.py <https://github.com/khornberg/octokit.py>`_
   (look for the "Fork" button).
2. Clone your fork locally::

    git clone git@github.com:your_name_here/octokit.py.git

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. When you're done making changes, run all the checks, doc builder and spell checker with `tox <http://tox.readthedocs.io/en/latest/install.html>`_ one command::

    tox

5. Commit your changes using the commit message guide and push your branch to GitHub::

    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature

6. Submit a pull request through the GitHub website.

Commit Message Guidelines
-------------------------

Prefix messages with one of the prefixes below followed by a colon:

Example message::

    Style: yapf

Bug Fix
    A fix for a bug
Feature
    Something that did not previously exist

Enhancement
    Something that previously existed, but now works slightly differently in some way
Doc
    Documentation
Version
    A new (semver) version number
Dependency
    Updating the dependencies
    Updating 3rd party APIs ect
Refactor
    Improvements to code with no modification of external behavior
    Include Performance Enhancements
Test
    New tests or altering old tests without changing any production code
    Helper code intended to assist ONLY with test creation
Style
    Linting violations, code formatting, etc
Peripheral
    Updates to builds, deploys, etc

Pull Request Guidelines
-----------------------

If you need some code review or feedback while you're developing the code just make the pull request.

For merging, you should:

1. Include passing tests (run ``tox``) [1]_.
2. Update documentation when there's new API, functionality etc.
4. Add yourself to ``AUTHORS.rst``.

.. [1] If you don't have all the necessary python versions available locally you can rely on Travis - it will
       `run the tests <https://travis-ci.org/khornberg/octokit.py/pull_requests>`_ for each change you add in the pull request.

       It will be slower though ...

Tips
----

To run a subset of tests::

    tox -e envname -- py.test -k test_myfeature

To run all the test environments in *parallel* (you need to ``pip install detox``)::

    detox
