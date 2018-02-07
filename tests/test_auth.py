import os
from collections import namedtuple

import pytest
import requests
from octokit import Octokit


class TestAuth(object):

    def test_can_set_basic_authentication(self):
        sut = Octokit(auth='basic', username='myuser', password='mypassword')
        assert sut.auth == 'basic'
        assert sut.username == 'myuser'
        assert sut.password == 'mypassword'

    def test_cannot_set_basic_authentication_with_out_required_data(self):
        with pytest.raises(KeyError):
            Octokit(auth='basic')
        with pytest.raises(AssertionError):
            Octokit(auth='basic', username='z', password='')
        with pytest.raises(KeyError):
            Octokit(auth='basic', password='mypassword')
        with pytest.raises(AssertionError):
            Octokit(auth='basic', username='')
        with pytest.raises(KeyError):
            Octokit(auth='basic', username='xyz')

    def test_basic_auth_used_if_set(self, mocker):
        mocker.patch('requests.get')
        Octokit(auth='basic', username='myuser', password='mypassword').authorization.get(id=100)
        requests.get.assert_called_once_with(
            'https://api.github.com/authorizations/100',
            params={},
            headers=Octokit().headers,
            auth=('myuser', 'mypassword')
        )

    def test_can_set_token_authentication(self):
        sut = Octokit(auth='token', token='yippy')
        assert sut.auth == 'token'
        assert sut.token == 'yippy'

    def test_cannot_set_token_authentication_with_out_required_data(self):
        with pytest.raises(KeyError):
            Octokit(auth='token')
        with pytest.raises(AssertionError):
            Octokit(auth='token', token='')

    def test_token_auth_used_if_set(self, mocker):
        mocker.patch('requests.get')
        Octokit(auth='token', token='yak').authorization.get(id=100)
        headers = {**Octokit().headers, 'Authorization': 'token yak'}
        requests.get.assert_called_once_with(
            'https://api.github.com/authorizations/100',
            params={},
            headers=headers,
        )

    def test_can_set_app_authentication(self, mocker):
        Request = namedtuple('Request', ['json'])
        get = mocker.patch('requests.get')
        get.return_value = Request(json=lambda: [{'id': 37}])
        post = mocker.patch('requests.post')
        post.return_value = Request(json=lambda: {'token': 'v1.1f699f1069f60', 'expires_at': '2016-07-11T22:14:10Z'})
        with open(os.path.join(os.path.dirname(__file__), 'test.pem'), 'r') as f:
            private_key = f.read()
        sut = Octokit(auth='app', app_id=42, private_key=private_key)
        assert sut.auth == 'app'
        assert sut.token == 'v1.1f699f1069f60'
        assert sut.expires_at == '2016-07-11T22:14:10Z'

    def test_cannot_set_app_authentication_with_out_required_data(self):
        with pytest.raises(KeyError):
            Octokit(auth='app')
        with pytest.raises(AssertionError):
            Octokit(auth='app', app_id='')
        with pytest.raises(KeyError):
            Octokit(auth='app', app_id=42)
        with pytest.raises(AssertionError):
            Octokit(auth='app', app_id=42, private_key='')

    def test_app_token_is_used_if_set(self, mocker):
        Request = namedtuple('Request', ['json'])
        get = mocker.patch('requests.get')
        get.return_value = Request(json=lambda: [{'id': 37}])
        post = mocker.patch('requests.post')
        post.return_value = Request(json=lambda: {'token': 'v1.1f699f1069f60', 'expires_at': '2016-07-11T22:14:10Z'})
        with open(os.path.join(os.path.dirname(__file__), 'test.pem'), 'r') as f:
            private_key = f.read()
        sut = Octokit(auth='app', app_id=42, private_key=private_key)
        get = mocker.patch('requests.get')
        sut.authorization.get(id=100)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'token v1.1f699f1069f60',
            'accept': 'application/vnd.github.machine-man-preview+json'
        }
        requests.get.assert_called_once_with(
            'https://api.github.com/authorizations/100',
            params={},
            headers=headers,
        )
