import json
from collections import namedtuple

import pytest
import requests
from octokit import Octokit
from octokit import errors


class TestClientMethods(object):

    def test_client_methods_are_lower_case(self):
        for client in Octokit().__dict__:
            try:
                cls = getattr(Octokit(), client).__dict__
                assert all(method.islower() for method in cls)
            except AttributeError:
                pass  # ignore non-class attributes

    def test_method_has_doc_string(self):
        assert Octokit().oauth_authorizations.list_grants.__doc__ == self.doc_string

    def test_method_has_name_string(self):
        assert Octokit().oauth_authorizations.list_grants.__name__ == 'list_grants'

    def test_method_is_accessible_also_by_snake_case_name(self):
        assert Octokit().oauth_authorizations.list_your_grants.__name__ == 'list_your_grants'

    def test_method_calls_requests(self, mocker):
        mocker.patch('requests.get')
        Octokit().oauth_authorizations.get_authorization(authorization_id=1)
        assert requests.get.called
        assert requests.get.call_count == 1

    def test_has_required_method_parameters(self):
        with pytest.raises(errors.OctokitParameterError) as e1:
            Octokit().oauth_authorizations.get_authorization()
        assert 'authorization_id is a required parameter' == str(e1.value)
        with pytest.raises(errors.OctokitParameterError) as e2:
            Octokit().oauth_authorizations.get_authorization(authorization_id=None)
        assert 'authorization_id must have a value' == str(e2.value)

    def test_only_allows_valid_method_parameters(self):
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().oauth_authorizations.list_grants(notvalid=1)
        assert 'None is not a valid parameter for notvalid' == str(e.value)

    def test_validate_method_parameters(self, mocker):
        mocker.patch('requests.get')
        Octokit().oauth_authorizations.get_authorization(authorization_id=100)
        requests.get.assert_called_once_with(
            'https://api.github.com/authorizations/100', params={}, headers=Octokit().headers
        )

    def test_request_has_body_parameters(self, mocker):
        mocker.patch('requests.post')
        data = {'note': 'remind me', 'scopes': ['public_repo']}
        create = Octokit().oauth_authorizations.create_authorization(**data)
        requests.post.assert_called_once_with(
            'https://api.github.com/authorizations', data=json.dumps(data, sort_keys=True), headers=create.headers
        )

    def test_must_include_required_body_parameters(self):
        data = {'gist_id': 'abc123', 'note': 'remind me'}
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().oauth_authorizations.create_authorization(**data)
        assert 'None is not a valid parameter for gist_id' == str(e.value)

    def test_must_include_required_dictionary_sub_parameters_when_used(self, mocker):
        mocker.patch('requests.get')
        data = {'owner': 'owner', 'repo': 'repo', 'name': 'name', 'head_sha': 'master', 'output': {}}
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().checks.create(**data)
        assert 'output.title is a required parameter' == str(e.value)
        data.update({'output': {'title': 'blah'}})
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().checks.create(**data)
        assert 'output.summary is a required parameter' == str(e.value)
        data.update({'output': {'title': 'blah', 'summary': 'that'}})
        Octokit().checks.create(**data)

    def test_must_include_required_list_sub_parameters_when_used(self, mocker):
        mocker.patch('requests.get')
        data = {'owner': 'owner', 'repo': 'repo', 'name': 'name', 'head_sha': 'master', 'actions': []}
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().checks.create(**data)
        assert 'actions.label is a required parameter' == str(e.value)
        data.update({'actions': {'label': 'blah'}})
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().checks.create(**data)
        assert 'actions.description is a required parameter' == str(e.value)
        data.update({'actions': {'label': 'blah', 'description': 'x', 'identifier': 'a'}})
        Octokit().checks.create(**data)

    def test_use_default_parameter_values(self, mocker):
        mocker.patch('requests.get')
        headers = {'Content-Type': 'application/json', 'accept': 'application/vnd.github.v3+json'}
        data = {'sort': 'created'}
        Octokit().issues.list_comments_for_repo(owner='testUser', repo='testRepo')
        requests.get.assert_called_once_with(
            'https://api.github.com/repos/testUser/testRepo/issues/comments', params=data, headers=headers
        )

    def test_use_passed_value_instead_of_default_parameter_values(self, mocker):
        mocker.patch('requests.get')
        headers = {'Content-Type': 'application/json', 'accept': 'application/vnd.github.v3+json'}
        data = {'sort': 'updated'}
        Octokit().issues.list_comments_for_repo(owner='testUser', repo='testRepo', **data)
        requests.get.assert_called_once_with(
            'https://api.github.com/repos/testUser/testRepo/issues/comments', params=data, headers=headers
        )

    def test_validate_enum_values(self):
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().issues.update(owner='testUser', repo='testRepo', number=1, state='closeddddd')
        assert 'closeddddd is not a valid option for state; must be one of [\'open\', \'closed\']' == str(e.value)

    def test_validate_boolean_values(self, mocker):
        mocker.patch('requests.post')
        Octokit().repos.create_deployment(owner='testUser', repo='testRepo', ref='abc123')
        data = '{"auto_merge": true, "description": "\\"\\"", "environment": "production", "payload": "\\"\\"", "production_environment": "`true` when `environment` is `production` and `false` otherwise", "ref": "abc123", "task": "deploy"}'  # noqa E501
        headers = {'Content-Type': 'application/json', 'accept': 'application/vnd.github.v3+json'}
        requests.post.assert_called_once_with(
            'https://api.github.com/repos/testUser/testRepo/deployments', data=data, headers=headers
        )

    def test_non_default_params_not_in_the_url_for_get_requests_go_in_the_query_string(self, mocker):
        mocker.patch('requests.get')
        params = {'page': 2, 'per_page': 30}
        Octokit().oauth_authorizations.list_grants(page=2)
        requests.get.assert_called_once_with(
            'https://api.github.com/applications/grants', params=params, headers=Octokit().headers
        )

    def test_use_previous_values_if_available(self, mocker):
        mocker.patch('requests.patch')
        mocker.patch('requests.post')
        headers = {'accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}
        data = {'state': 'closed'}
        issue = Octokit().issues.update(owner='testUser', repo='testRepo', issue_number=1, **data)
        requests.patch.assert_called_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )
        issue2 = issue.issues.update(**data)
        requests.patch.assert_called_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )
        issue2.pulls.create(head='branch', base='master', title='Title')
        requests.post.assert_called_with(
            'https://api.github.com/repos/testUser/testRepo/pulls',
            data=json.dumps({
                'base': 'master',
                'head': 'branch',
                'title': 'Title',
            }, sort_keys=True),
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/vnd.github.v3+json'
            }
        )

    def test_can_override_previous_values(self, mocker):
        mocker.patch('requests.patch')
        mocker.patch('requests.post')
        headers = {'accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}
        data = {'state': 'closed'}
        issue = Octokit().issues.update(owner='testUser', repo='testRepo', issue_number=1, **data)
        requests.patch.assert_called_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )
        issue.pulls.create(owner='user', head='branch', base='master', title='Title')
        requests.post.assert_called_with(
            'https://api.github.com/repos/user/testRepo/pulls',
            data=json.dumps({
                'base': 'master',
                'head': 'branch',
                'title': 'Title',
            }, sort_keys=True),
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/vnd.github.v3+json'
            }
        )

    def test_returned_object_is_not_self_but_a_copy_of_self(self, mocker):
        mocker.patch('requests.patch')
        headers = {'accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}
        octokit = Octokit()
        sut = octokit.issues.update(owner='testUser', repo='testRepo', issue_number=1)
        requests.patch.assert_called_once_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data='{}', headers=headers
        )
        assert sut.__class__.__name__ == 'Octokit'
        assert sut != octokit

    def test_returned_object_has_requests_response_object(self, mocker):
        patch = mocker.patch('requests.patch')
        Response = namedtuple('Response', ['json'])
        patch.return_value = Response(json=lambda: {})
        sut = Octokit().issues.update(owner='testUser', repo='testRepo', issue_number=1)
        assert sut._response.__class__.__name__ == 'Response'

    def test_returned_object_has_json_attribute(self, mocker):
        patch = mocker.patch('requests.patch')
        Request = namedtuple('Request', ['json'])
        patch.return_value = Request(json=lambda: data)
        data = {
            'documentation_url': 'https://developer.github.com/v3/issues/#get-a-single-issue',
            'message': 'Not Found'
        }
        sut = Octokit().issues.get(owner='testUser', repo='testRepo', issue_number=1)
        assert sut.json == data

    def test_returned_object_has_response_attributes(self, mocker):
        patch = mocker.patch('requests.patch')
        data = {
            "id": 1,
            "number": 1347,
            "state": "open",
            "title": "Found a bug",
            "user": {
                "login": "octocat",
                "site_admin": False
            },
            "labels": [{
                "id": 208045946,
            }, {
                "id": 208045947,
            }],
        }
        Request = namedtuple('Request', ['json'])
        patch.return_value = Request(json=lambda: data)
        sut = Octokit().issues.update(owner='testUser', repo='testRepo', issue_number=1)
        assert sut.response.id == 1
        assert sut.response.number == 1347
        assert sut.response.state == 'open'
        assert str(sut.response.user) == '<class \'octokit.ResponseData\'>'
        assert sut.response.user.login == 'octocat'
        assert sut.response.user.site_admin is False
        assert sut.response.labels[0].id == 208045946

    def test_returned_object_is_a_list(self, mocker):
        patch = mocker.patch('requests.patch')
        data = [{
            "id": 208045946,
        }, {
            "id": 208045947,
        }]
        Request = namedtuple('Request', ['json'])
        patch.return_value = Request(json=lambda: data)
        sut = Octokit().issues.update(owner='testUser', repo='testRepo', issue_number=1)
        assert sut.response[0].id == 208045946

    def test_an_exception_with_json_is_replaced_by_the_raw_text(self, mocker):
        patch = mocker.patch('requests.patch')
        Request = namedtuple('Request', ['json'])
        patch.return_value = Request(json=lambda: 'test')
        sut = Octokit().issues.update(owner='testUser', repo='testRepo', issue_number=1)
        assert sut.json == 'test'

    def test_can_pass_in_optional_headers(self, mocker):
        mocker.patch('requests.get')
        headers = {'accept': 'application/vnd.github.ant-man-preview+json', 'Content-Type': 'application/json'}
        Octokit().oauth_authorizations.get_authorization(
            authorization_id=100, headers={
                'accept': 'application/vnd.github.ant-man-preview+json'
            }
        )
        requests.get.assert_called_once_with('https://api.github.com/authorizations/100', params={}, headers=headers)

    def test_dictionary_keys_are_validated(self, mocker):
        mocker.patch('requests.put')
        headers = {'accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}
        data = {
            "required_status_checks": {
                "strict": True,
                "contexts": [],
            },
            "required_pull_request_reviews": {
                "dismiss_stale_reviews": True
            },
            "enforce_admins": True,
            "restrictions": {
                "users": [],
                "teams": [],
            }
        }
        Octokit().repos.update_branch_protection(owner='user', repo='repo', branch='branch', **data)
        requests.put.assert_called_with(
            'https://api.github.com/repos/user/repo/branches/branch/protection',
            data=json.dumps(data, sort_keys=True),
            headers=headers
        )

    @property
    def doc_string(self):
        return """You can use this API to list the set of OAuth applications that have been granted access to your account. Unlike the [list your authorizations](https://developer.github.com/v3/oauth_authorizations/#list-your-authorizations) API, this API does not manage individual tokens. This API will return one entry for each OAuth application that has been granted access to your account, regardless of the number of tokens an application has generated for your user. The list of OAuth applications returned matches what is shown on [the application authorizations settings screen within GitHub](https://github.com/settings/applications#authorized). The `scopes` returned are the union of scopes authorized for the application. For example, if an application has one token with `repo` scope and another token with `user` scope, the grant will return `[\"repo\", \"user\"]`."""  # noqa E501
