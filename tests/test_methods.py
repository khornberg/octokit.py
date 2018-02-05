from octokit import Octokit
import requests
import pytest


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
        Octokit().authorization.get()
        assert requests.get.called
        assert requests.get.call_count == 1

    def test_has_required_method_parameters(self, mocker):
        with pytest.raises(AssertionError):
            Octokit().authorization.get()
        with pytest.raises(AssertionError):
            Octokit().authorization.get(id=None)

    def test_only_allows_valid_method_parameters(self, mocker):
        with pytest.raises(AssertionError):
            Octokit().authorization.get_grants(notvalid=1)

    def test_validate_method_parameters(self, mocker):
        mocker.patch('requests.get')
        Octokit().authorization.get(id=100)
        requests.get.assert_called_once_with('https://api.github.com/authorizations/100', data=None, headers={})
