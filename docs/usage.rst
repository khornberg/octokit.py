=====
Usage
=====

To use octokit.py in a project::

    import octokit

Chaining requests
=================

::

    issue = Octokit().issues.edit(owner='testUser', repo='testRepo', number=1, state='closed')
    # If the previous request had a required url attribute, the next request will use the previous url attribute
    # This does not apply attributes that are part of the body of the request on post, patch, etc.
    issue.pull_requests.create(head='branch', base='master', title='Title')
    # Previous attributes can be overridden
    issue.pull_requests.create(owner='differentOwner', head='branch', base='master', title='Title')

Responses
=========

Responses are the Octokit instance with state in ``json`` and  ``response``. ``json`` is the result of the Requests ``response.json()``. ``response`` is the json as a python object.


octokit.json
================

::

    issue = Octokit().issues.get(owner='testUser', repo='testRepo', number=1)
    issue.json['title']  # Title of issue


octokit.response
================

::

    issue = Octokit().issues.get(owner='testUser', repo='testRepo', number=1)
    issue.response.title  # Title of issue
