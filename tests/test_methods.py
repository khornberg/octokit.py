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
            except AttributeError:
                pass  # ignore non-class attributes
            assert all(method.islower() for method in cls)

    def test_method_has_doc_string(self):
        assert Octokit().authorization.get.__doc__ == 'Get a single authorization.'

    def test_method_has_name_string(self):
        assert Octokit().authorization.get.__name__ == 'get'

    def test_method_calls_requests(self, mocker):
        mocker.patch('requests.get')
        Octokit().authorization.get(id=1)
        assert requests.get.called
        assert requests.get.call_count == 1

    def test_has_required_method_parameters(self):
        with pytest.raises(errors.OctokitParameterError) as e1:
            Octokit().authorization.get()
        assert 'id is a required parameter' == str(e1.value)
        with pytest.raises(errors.OctokitParameterError) as e2:
            Octokit().authorization.get(id=None)
        assert 'id must have a value' == str(e2.value)

    def test_only_allows_valid_method_parameters(self):
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().authorization.get_grants(notvalid=1)
        assert 'None is not a valid parameter for notvalid' == str(e.value)

    def test_validate_method_parameters(self, mocker):
        mocker.patch('requests.get')
        Octokit().authorization.get(id=100)
        requests.get.assert_called_once_with(
            'https://api.github.com/authorizations/100', params={}, headers=Octokit().headers
        )

    def test_request_has_body_parameters(self, mocker):
        mocker.patch('requests.post')
        data = {'scopes': ['public_repo']}
        create = Octokit().authorization.create(**data)
        requests.post.assert_called_once_with(
            'https://api.github.com/authorizations', data=json.dumps(data), headers=create.headers
        )

    def test_must_include_required_body_parameters(self):
        data = {'gist_id': 'abc123'}
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().authorization.create(**data)
        assert 'None is not a valid parameter for gist_id' == str(e.value)

    def test_use_default_parameter_values(self, mocker):
        mocker.patch('requests.patch')
        headers = {'accept': 'application/vnd.github.squirrel-girl-preview', 'Content-Type': 'application/json'}
        data = {'state': 'open'}
        Octokit().issues.edit(owner='testUser', repo='testRepo', number=1)
        requests.patch.assert_called_once_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )

    def test_use_passed_value_instead_of_default_parameter_values(self, mocker):
        mocker.patch('requests.patch')
        headers = {'accept': 'application/vnd.github.squirrel-girl-preview', 'Content-Type': 'application/json'}
        data = {'state': 'closed'}
        Octokit().issues.edit(owner='testUser', repo='testRepo', number=1, **data)
        requests.patch.assert_called_once_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )

    def test_validate_enum_values(self):
        with pytest.raises(errors.OctokitParameterError) as e:
            Octokit().issues.edit(owner='testUser', repo='testRepo', number=1, state='closeddddd')
        assert 'closeddddd is not a valid option for state; must be one of [\'open\', \'closed\']' == str(e.value)

    def test_non_default_params_not_in_the_url_for_get_requests_go_in_the_query_string(self, mocker):
        mocker.patch('requests.get')
        params = {'page': 2, 'per_page': '30'}
        Octokit().authorization.get_grant(id=404, page=2)
        requests.get.assert_called_once_with(
            'https://api.github.com/applications/grants/404', params=params, headers=Octokit().headers
        )

    def test_use_previous_values_if_available(self, mocker):
        mocker.patch('requests.patch')
        mocker.patch('requests.post')
        headers = {'accept': 'application/vnd.github.squirrel-girl-preview', 'Content-Type': 'application/json'}
        data = {'state': 'closed'}
        issue = Octokit().issues.edit(owner='testUser', repo='testRepo', number=1, **data)
        requests.patch.assert_called_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )
        issue2 = issue.issues.edit(**data)
        requests.patch.assert_called_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )
        issue2.pull_requests.create(head='branch', base='master', title='Title')
        requests.post.assert_called_with(
            'https://api.github.com/repos/testUser/testRepo/pulls',
            data=json.dumps({
                'base': 'master',
                'head': 'branch',
                'title': 'Title',
            }, sort_keys=True),
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/vnd.github.machine-man-preview+json'
            }
        )

    def test_can_override_previous_values(self, mocker):
        mocker.patch('requests.patch')
        mocker.patch('requests.post')
        headers = {'accept': 'application/vnd.github.squirrel-girl-preview', 'Content-Type': 'application/json'}
        data = {'state': 'closed'}
        issue = Octokit().issues.edit(owner='testUser', repo='testRepo', number=1, **data)
        requests.patch.assert_called_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )
        issue.pull_requests.create(owner='user', head='branch', base='master', title='Title')
        requests.post.assert_called_with(
            'https://api.github.com/repos/user/testRepo/pulls',
            data=json.dumps({
                'base': 'master',
                'head': 'branch',
                'title': 'Title',
            }, sort_keys=True),
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/vnd.github.machine-man-preview+json'
            }
        )

    def test_returned_object_is_not_self_but_a_copy_of_self(self, mocker):
        mocker.patch('requests.patch')
        headers = {'accept': 'application/vnd.github.squirrel-girl-preview', 'Content-Type': 'application/json'}
        data = {'state': 'open'}
        octokit = Octokit()
        sut = octokit.issues.edit(owner='testUser', repo='testRepo', number=1)
        requests.patch.assert_called_once_with(
            'https://api.github.com/repos/testUser/testRepo/issues/1', data=json.dumps(data), headers=headers
        )
        assert sut.__class__.__name__ == 'Octokit'
        assert sut != octokit

    def test_returned_object_has_requests_response_object(self, mocker):
        patch = mocker.patch('requests.patch')
        Response = namedtuple('Response', ['json'])
        patch.return_value = Response(json=lambda: {})
        sut = Octokit().issues.edit(owner='testUser', repo='testRepo', number=1)
        assert sut._response.__class__.__name__ == 'Response'

    def test_returned_object_has_json_attribute(self, mocker):
        patch = mocker.patch('requests.patch')
        Request = namedtuple('Request', ['json'])
        patch.return_value = Request(json=lambda: data)
        data = {'documentation_url': 'https://developer.github.com/v3', 'message': 'Not Found'}
        sut = Octokit().issues.edit(owner='testUser', repo='testRepo', number=1)
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
        sut = Octokit().issues.edit(owner='testUser', repo='testRepo', number=1)
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
        sut = Octokit().issues.edit(owner='testUser', repo='testRepo', number=1)
        assert sut.response[0].id == 208045946

    def test_an_exception_with_json_is_replaced_by_the_raw_text(self, mocker):
        patch = mocker.patch('requests.patch')
        Request = namedtuple('Request', ['json'])
        patch.return_value = Request(json=lambda: 'test')
        sut = Octokit().issues.edit(owner='testUser', repo='testRepo', number=1)
        assert sut.json == 'test'
