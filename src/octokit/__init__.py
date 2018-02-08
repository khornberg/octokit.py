import datetime
import json
import re
from collections import ChainMap

import requests
from jose import jwt
from octokit import utils


class Base(object):

    headers = {'accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}
    base_url = 'https://api.github.com'

    def _get_headers(self, definition):
        return dict(ChainMap(definition.get('headers', {}), self.headers))

    def _validate(self, kwargs, params):
        required_params = [k for k, v in params.items() if v.get('required')]
        for p in required_params:
            assert p in kwargs  # has all required
        for kwarg, value in kwargs.items():
            param_value = params.get(kwarg)
            assert param_value  # is a valid param but not necessarily required
            if param_value.get('enum'):
                assert value in param_value.get('enum')  # is a valid option of the enum
            if kwarg in required_params:
                assert value  # required param has a value

    def _form_url(self, values, _url):
        data_values = values.copy()
        for name, value in values.items():
            _url, subs = re.subn(f':{name}', str(value), _url)
            if subs != 0:
                data_values.pop(name)
        url = f'{self.base_url}{_url}'
        return url, data_values

    def _get_data(self, kwargs, params):
        for param, value in params.items():
            if value.get('default') and not kwargs.get(param):
                kwargs[param] = value.get('default')
        return kwargs

    def _data(self, data_kwargs, params, method):
        data = self._get_data(data_kwargs, params)
        if method == 'get':
            return {'params': data}
        if method in ['post', 'patch', 'put', 'delete']:
            return {'data': json.dumps(data)}
        return {}

    def _setup_authentication(self, kwargs):
        authentication_schemes = {
            'basic': self._setup_basic_authentication,
            'token': self._setup_token_authentication,
            'app': self._setup_app_authentication,
        }
        if kwargs.get('auth'):
            authentication_schemes.get(kwargs.get('auth'))(kwargs)

    def _setup_basic_authentication(self, kwargs):
        assert kwargs['username']
        assert kwargs['password']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.auth = kwargs['auth']

    def _setup_token_authentication(self, kwargs):
        assert kwargs['token']
        self.token = kwargs['token']
        self.auth = kwargs['auth']

    def _setup_app_authentication(self, kwargs):
        assert kwargs['app_id']
        assert kwargs['private_key']
        self.token, self.expires_at = self._app_auth_get_token(kwargs['app_id'], kwargs['private_key'])
        self.auth = kwargs['auth']
        self.headers['accept'] = 'application/vnd.github.machine-man-preview+json'

    def _app_auth_get_token(self, app_id, key):
        headers = {
            'Authorization': 'Bearer {}'.format(self._app_auth_get_jwt(app_id, key)),
            'Accept': 'application/vnd.github.machine-man-preview+json',
        }
        installation_url = f'{self.base_url}/app/installations'
        installations = requests.get(installation_url, headers=headers).json()
        installation_id = installations[0]['id']
        installation_token_url = f'{self.base_url}/installations/{installation_id}/access_tokens'
        response = requests.post(installation_token_url, headers=headers).json()
        return response['token'], response['expires_at']

    def _app_auth_get_jwt(self, app_id, key):
        payload = {
            'iat': int(datetime.datetime.timestamp(datetime.datetime.now())),
            'exp': int(datetime.datetime.timestamp(datetime.datetime.now())) + (10 * 60),
            'iss': app_id,
        }
        return jwt.encode(payload, key, algorithm='RS256')

    def _auth(self, requests_kwargs):
        if getattr(self, 'auth', None) == 'basic':
            return {'auth': (self.username, self.password)}
        if getattr(self, 'auth', None) in ['token', 'app']:
            headers = requests_kwargs['headers']
            headers.update({'Authorization': f'token {self.token}'})
            return {'headers': headers}
        return {}


class Octokit(Base):

    def __init__(self, *args, **kwargs):
        self._create(utils.get_json_data('rest.json'))
        self._setup_authentication(kwargs)

    def _create(self, definitions):
        for name, value in definitions.items():
            cls_name = utils.snake_case(name)
            client = self._create_client(cls_name, value)
            setattr(self, cls_name, client)

    def _create_client(self, name, methods):
        class_attributes = {}
        for _name, method in methods.items():
            method_name = utils.snake_case(str(_name))
            class_attributes.update({method_name: self._create_method(method_name, method)})
        bases = [object]
        cls = type(name, tuple(bases), class_attributes)
        return cls

    def _create_method(self, name, definition):

        def _api_call(*args, **kwargs):
            self._validate(kwargs, definition.get('params'))
            method = definition['method'].lower()
            requests_kwargs = {'headers': self._get_headers(definition)}
            url, data_kwargs = self._form_url(kwargs, definition['url'])
            requests_kwargs.update(self._data(data_kwargs, definition.get('params'), method))
            requests_kwargs.update(self._auth(requests_kwargs))
            return getattr(requests, method)(url, **requests_kwargs)

        _api_call.__name__ = name
        _api_call.__doc__ = definition['description']
        return _api_call
