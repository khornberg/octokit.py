import copy
import datetime
import json
import re
from collections import ChainMap
from collections import defaultdict

import requests
from jose import jwt
from octokit import errors
from octokit import utils
from routes import specifications

page_regex = re.compile(r'[\?\&]page=(\d+)[_&=%+\w\d]*>; rel="(\w+)"')


class Base(object):

    base_url = 'https://api.github.com'

    def __init__(self):
        self.headers = {'accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}

    def _get_headers(self, method_headers):
        return dict(ChainMap(method_headers, self.headers))

    def _get_required_params(self, params, cached_kwargs):
        all_required = [k for k, v in params.items() if v.get('required')]
        required_params = []
        for p in all_required:
            param = p.replace('[]', '')
            if utils.verify_path(cached_kwargs, param.split('.')):
                required_params.append(param)
        return required_params

    def _validate(self, kwargs, params):
        cached_kwargs = dict(ChainMap(kwargs, self._attribute_cache['url']))
        required_params = self._get_required_params(params, cached_kwargs)
        self._validate_required_params(required_params, cached_kwargs)
        for kwarg, value in kwargs.items():
            param_value = params.get(kwarg)
            self._validate_params(param_value, kwarg, value, required_params)

    def _raise_required_parameter(self, param):
        message = '{} is a required parameter'.format(param)
        raise errors.OctokitParameterError(message)

    def _validate_required_params(self, required_params, cached_kwargs):
        for p in required_params:
            try:
                utils.walk_path(cached_kwargs, p.split('.'))
            except KeyError:
                self._raise_required_parameter(p)
            except AssertionError:
                self._raise_required_parameter(p)

    def _validate_params(self, param_value, kwarg, value, required_params):
        if not param_value:  # is a valid param but not necessarily required
            message = '{} is not a valid parameter for {}'.format(param_value, kwarg)
            raise errors.OctokitParameterError(message)
        if param_value.get('enum') and value not in param_value.get('enum'):  # is a valid option of the enum
            message = '{} is not a valid option for {}; must be one of {}'.format(value, kwarg, param_value.get('enum'))
            raise errors.OctokitParameterError(message)
        if kwarg in required_params and not value:  # required param has a value
            message = '{} must have a value'.format(kwarg)
            raise errors.OctokitParameterError(message)

    def _form_url(self, values, _url, params):
        _values = dict(ChainMap(values, self._attribute_cache['url']))
        filtered_kwargs = {k: v for k, v in _values.items() if params.get(k)}
        data_values = filtered_kwargs.copy()
        for name, value in filtered_kwargs.items():
            _url, subs = re.subn(':{}'.format(name), str(value), _url)
            if subs != 0:
                self._attribute_cache['url'][name] = data_values.pop(name)
        url = '{}{}'.format(self.base_url, _url)
        return url, data_values

    def _get_data(self, kwargs, params):
        for param, value in params.items():
            if value.get('default') and not kwargs.get(param):
                kwargs[param] = self._get_parameter_for_type(value)
        return kwargs

    def _get_parameter_for_type(self, param):
        if param.get('type') == 'boolean' and param.get('default') == 'true':
            return True
        if param.get('type') == 'boolean' and param.get('default') == 'false':
            return False
        return param.get('default')

    def _data(self, data_kwargs, params, method):
        data = self._get_data(data_kwargs, params)
        if method == 'get':
            return {'params': data}
        if method in ['post', 'patch', 'put', 'delete']:
            return {'data': json.dumps(data, sort_keys=True)}
        return {}

    def _setup_authentication(self, kwargs):
        authentication_schemes = {
            'basic': self._setup_basic_authentication,
            'token': self._setup_token_authentication,
            'installation': self._setup_installation_authentication,
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

    def _setup_installation_authentication(self, kwargs):
        assert kwargs['app_id']
        assert kwargs['private_key']
        self.token, self.expires_at = self._app_auth_get_token(kwargs['app_id'], kwargs['private_key'])
        self.auth = kwargs['auth']
        self.headers['accept'] = 'application/vnd.github.machine-man-preview+json'

    def _setup_app_authentication(self, kwargs):
        assert kwargs['app_id']
        assert kwargs['private_key']
        self.jwt = self._app_auth_get_jwt(kwargs['app_id'], kwargs['private_key'])
        self.auth = kwargs['auth']
        self.headers['accept'] = 'application/vnd.github.machine-man-preview+json'

    def _app_auth_get_token(self, app_id, key):
        headers = {
            'Authorization': 'Bearer {}'.format(self._app_auth_get_jwt(app_id, key)),
            'Accept': 'application/vnd.github.machine-man-preview+json',
        }
        installation_url = '{}/app/installations'.format(self.base_url)
        installations = requests.get(installation_url, headers=headers).json()
        self.installation_id = [x.get('id') for x in installations if str(x.get('app_id')) == app_id].pop()
        installation_token_url = '{}/installations/{}/access_tokens'.format(self.base_url, self.installation_id)
        response = requests.post(installation_token_url, headers=headers).json()
        return response['token'], response['expires_at']

    def _app_auth_get_jwt(self, app_id, key):
        payload = {
            'iat': int(datetime.datetime.timestamp(datetime.datetime.now())),
            'exp': int(datetime.datetime.timestamp(datetime.datetime.now())) + (9 * 60),
            'iss': app_id,
        }
        return jwt.encode(payload, key, algorithm='RS256')

    def _auth(self, requests_kwargs):
        if getattr(self, 'auth', None) == 'basic':
            return {'auth': (self.username, self.password)}
        if getattr(self, 'auth', None) in ['app', 'token', 'installation']:
            _headers = {
                'app': {
                    'Authorization': 'Bearer {}'.format(getattr(self, 'jwt', None))
                },
                'token': {
                    'Authorization': 'token {}'.format(getattr(self, 'token', None))
                },
                'installation': {
                    'Authorization': 'token {}'.format(getattr(self, 'token', None))
                },
            }
            headers = requests_kwargs['headers']
            headers.update(_headers.get(getattr(self, 'auth', None)))
            return {'headers': headers}
        return {}


class Octokit(Base):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._create(specifications[kwargs.get('routes', 'api.github.com')])
        self._setup_authentication(kwargs)
        self._attribute_cache = defaultdict(dict)

    def _create(self, definitions):
        for name, value in definitions.items():
            cls_name = utils.snake_case(name)
            client = self._create_client(cls_name, value)
            setattr(self, cls_name, client)

    def _create_client(self, name, methods):
        class_attributes = {}
        for method in methods:
            for method_name in [utils.snake_case(str(method['name'])), utils.snake_case(str(method['idName']))]:
                class_attributes.update({method_name: self._create_method(method_name, method)})
        bases = [object]
        cls = type(name, tuple(bases), class_attributes)
        return cls

    def _create_method(self, name, definition):

        def _api_call(*args, **kwargs):
            method_headers = kwargs.pop('headers') if kwargs.get('headers') else {}
            parameter_map = utils.parameter_transform(definition.get('params'))
            self._validate(kwargs, parameter_map)
            method = definition['method'].lower()
            requests_kwargs = {'headers': self._get_headers(method_headers)}
            url, data_kwargs = self._form_url(kwargs, definition['path'], parameter_map)
            requests_kwargs.update(self._data(data_kwargs, parameter_map, method))
            requests_kwargs.update(self._auth(requests_kwargs))
            _response = getattr(requests, method)(url, **requests_kwargs)
            try:
                attributes = _response.json()
            except ValueError:
                attributes = _response.text
            new_self = copy.deepcopy(self)
            setattr(new_self, '_response', _response)
            setattr(new_self, 'json', attributes)
            setattr(new_self, 'response', new_self._convert_to_object(attributes))
            return new_self

        _api_call.__name__ = name
        _api_call.__doc__ = definition['description']
        return _api_call

    def _convert_to_object(self, item):
        if isinstance(item, dict):
            return type('ResponseData', (object, ), {k: self._convert_to_object(v) for k, v in item.items()})
        if isinstance(item, list):
            return list((self._convert_to_object(value) for index, value in enumerate(item)))
        else:
            return item

    def set_pages(self, obj, previous_page_requested=None):
        response_headers = obj._response.headers
        links = response_headers.get('Link', None)
        if links:
            matches = re.findall(page_regex, links)
            if matches:
                for page, kind in matches:
                    setattr(obj, '{}_page'.format(kind), int(page))
                setattr(obj, 'pages', getattr(obj, 'last_page', previous_page_requested))
                setattr(obj, 'has_pages', True)
                setattr(obj, 'current_page', previous_page_requested or getattr(obj, 'next_page') - 1)
                setattr(obj, 'is_last_page', obj.pages == obj.current_page)
            else:
                setattr(obj, 'has_pages', False)
        return obj

    def paginate(self, obj, page=1, **kwargs):
        response = self.set_pages(obj(page=page, **kwargs))
        yield response.json
        if hasattr(response, 'is_last_page'):
            while not response.is_last_page:
                response = self.set_pages(obj(page=response.next_page, **kwargs), response.next_page)
                yield response.json
