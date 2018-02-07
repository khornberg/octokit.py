import json

import pytest
import requests
from octokit import Octokit


class TestClientMethods(object):

    def test_client_methods_are_lower_case(self):
        for client in Octokit().__dict__:
            assert all(method.islower() for method in getattr(Octokit(), client).__dict__)

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
        with pytest.raises(AssertionError):
            Octokit().authorization.get()
        with pytest.raises(AssertionError):
            Octokit().authorization.get(id=None)

    def test_only_allows_valid_method_parameters(self):
        with pytest.raises(AssertionError):
            Octokit().authorization.get_grants(notvalid=1)

    def test_validate_method_parameters(self, mocker):
        mocker.patch('requests.get')
        Octokit().authorization.get(id=100)
        requests.get.assert_called_once_with(
            'https://api.github.com/authorizations/100', params={}, headers=Octokit().headers
        )

    def test_request_has_body_parameters(self, mocker):
        mocker.patch('requests.post')
        data = {'scopes': ['public_repo'], 'note': 'admin script'}
        Octokit().authorization.create(**data)
        requests.post.assert_called_once_with(
            'https://api.github.com/authorizations', data=json.dumps(data), headers=Octokit().headers
        )

    def test_must_include_required_body_parameters(self):
        data = {'gist_id': 'abc123'}
        with pytest.raises(AssertionError):
            Octokit().authorization.create(**data)

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
        with pytest.raises(AssertionError):
            Octokit().issues.edit(owner='testUser', repo='testRepo', number=1, state='closeddddd')

    def test_non_default_params_not_in_the_url_for_get_requests_go_in_the_query_string(self, mocker):
        mocker.patch('requests.get')
        params = {'page': 2, 'per_page': '30'}
        Octokit().authorization.get_grant(id=404, page=2)
        requests.get.assert_called_once_with(
            'https://api.github.com/applications/grants/404', params=params, headers=Octokit().headers
        )
