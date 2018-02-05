import os
import re
import json
from collections import ChainMap
import requests
from octokit import utils

__version__ = '0.1.0'


class Base(object):

    headers = {}
    base_url = 'https://api.github.com'

    def _get_headers(self, definition):
        return dict(ChainMap(definition.get('headers', {}), self.headers))

    def _validate(self, kwargs, params):
        required_params = [k for k, v in params.items() if v.get('required')]
        for p in required_params:
            assert p in kwargs  # has all required
        for kwarg, value in kwargs.items():
            param = params.get(kwarg)
            assert param  # is a valid param but not necessarily required
            if kwarg in required_params:
                assert value  # required param has a value

    def _form_url(self, values, _url):
        data_values = values.copy()
        for name, value in values.items():
            _url, subs = re.subn(f':{name}', str(value), _url)
            if subs != 0:
                # TODO
                # it seems like params not in the url are in the body data
                data_values.pop(name)
        url = f'{self.base_url}{_url}'
        return url, data_values


class Octokit(Base):

    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'rest.json'), 'r') as f:
            definitions = json.load(f)
        self._create(definitions)

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
            url, data_kwargs = self._form_url(kwargs, definition['url'])
            # TODO for post, put, patch data
            # use defaults for params
            # data = json.dumps(o_kwargs) if o_kwargs else None
            data = None
            return getattr(requests, definition['method'].lower())(
                url, headers=self._get_headers(definition), data=data
            )
            pass

        _api_call.__name__ = name
        _api_call.__doc__ = definition['description']
        return _api_call
