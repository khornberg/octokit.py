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


class Base(object):

    base_url = "https://api.github.com"

    def __init__(self):
        self.headers = {"accept": "application/vnd.github.v3+json", "Content-Type": "application/json"}
        self._attribute_cache = defaultdict(dict)

    def _get_headers(self, method_headers):
        return dict(ChainMap(method_headers, self.headers))

    def _get_required_params(self, params, cached_kwargs):
        all_required = [k for k, v in params.items() if v.get("required")]
        required_params = all_required
        return required_params

    def validate(self, parameters, definition):
        self.validate_required_parameters(parameters, self.get_required_parameters(definition))
        schema = {}
        if definition.get("requestBody"):
            schema = definition["requestBody"]["content"]["application/json"]["schema"]
            self.validate_schema(parameters, schema)
        properties = schema.get("properties", {})
        valid_parameters = [p["name"] for p in definition.get("parameters")] + list(properties.keys())
        self.validate_other_parameters(parameters, valid_parameters, properties)
        return True

    def validate_other_parameters(self, parameters, valid_parameters, properties):
        for parameter, value in parameters.items():
            try:
                assert parameter in valid_parameters
            except AssertionError:
                message = "{} is not a valid parameter".format(parameter)
                raise errors.OctokitParameterError(message)
            if properties.get(parameter):
                self.validate_enum(parameter, value, properties)

    def validate_enum(self, parameter, value, properties):
        if properties.get(parameter).get("enum") and value not in properties.get(parameter).get("enum"):
            message = "{} is not a valid option for {}; must be one of {}".format(
                value, parameter, properties.get(parameter).get("enum")
            )
            raise errors.OctokitParameterError(message)

    def validate_schema(self, parameters, schema):
        if isinstance(parameters, list):
            self.validate_list(parameters, schema)
        if isinstance(parameters, dict):
            self.validate_dict(parameters, schema)
        self.validate_required_parameters(parameters, self.get_required_schema_properties(schema))
        self.type_match(parameters, schema.get("type"))

    def validate_dict(self, parameters, schema):
        for parameter, value in parameters.items():
            if isinstance(value, dict):
                self.validate_schema(value, schema.get("properties").get(parameter))
            if isinstance(value, list):
                self.validate_schema(value, schema.get("properties").get(parameter))

    def validate_list(self, parameters, schema):
        if not parameters and schema.get("items").get("required"):
            message = "property is missing required items"
            raise errors.OctokitParameterError(message)
        for parameter in parameters:
            self.validate_schema(parameter, schema.get("items", schema))

    def type_match(self, symbol, expected_type):
        types = {"array": list, "object": dict, "string": str}
        if not isinstance(symbol, types.get(expected_type)):
            name = symbol.__class__.__name__
            message = f"{name} type does not match the schema type of {expected_type} for the data of {symbol}"
            raise errors.OctokitParameterError(message)

    def get_required_schema_properties(self, schema):
        if schema.get("type") == "object":
            return schema.get("required")

    def get_required_parameters(self, definition):
        return [p.get("name") for p in definition.get("parameters") if p.get("required") and p.get("in") in ["path"]]

    def validate_required_parameters(self, parameters, required_parameters):
        for required_parameter in required_parameters or []:
            try:
                assert required_parameter in parameters
            except AssertionError:
                self._raise_required_parameter(required_parameter)
            if parameters[required_parameter] is None:
                self._raise_must_have_value(required_parameter)

    def _raise_required_parameter(self, param):
        message = "{} is a required parameter".format(param)
        raise errors.OctokitParameterError(message)

    def _raise_must_have_value(self, required_parameter):
        message = "{} must have a value".format(required_parameter)
        raise errors.OctokitParameterError(message)

    def _form_url(self, values, _url, params):
        _values = dict(ChainMap(values, self._attribute_cache["url"]))
        filtered_kwargs = {k: v for k, v in _values.items() if params.get(k)}
        data_values = filtered_kwargs.copy()
        for name, value in filtered_kwargs.items():
            _url, subs = re.subn(fr"{{{name}}}", str(value), _url)
            if subs != 0:
                self._attribute_cache["url"][name] = data_values.pop(name)
        url = "{}{}".format(self.base_url, _url)
        return url, data_values

    def _get_data(self, kwargs, params):
        data = array_data = {}
        for parameter_name, parameter in params.items():
            if parameter.get("type") == "array":
                array_data = self._get_array_data(parameter_name, parameter, kwargs)
            data.update(self._get_default_data(parameter_name, parameter, kwargs))
        return dict(ChainMap(data, array_data, kwargs))

    def _get_default_data(self, parameter_name, parameter, kwargs):
        data = {}
        if parameter.get("in") in ["query", "body"] and not kwargs.get(parameter_name):
            if parameter.get("schema", parameter).get("default") is not None:
                data[parameter_name] = self._get_parameter_for_type(parameter.get("schema", parameter))
        return data

    def _get_array_data(self, parameter_name, parameter, kwargs):
        data = {}
        properties = parameter.get("items", parameter).get("properties")
        if properties:
            for name, property_data in properties.items():
                if property_data.get("default") and not kwargs.get(parameter_name):
                    data[parameter_name] = self._get_parameter_for_type(property_data)
        return data

    def _get_parameter_for_type(self, schema):
        if schema.get("type") == "boolean" and schema.get("default") == "true":
            return True
        if schema.get("type") == "boolean" and schema.get("default") == "false":
            return False
        return schema.get("default")

    def _data(self, data_kwargs, params, method):
        data = self._get_data(data_kwargs, params)
        if method == "get":
            return {"params": data}
        if method in ["post", "patch", "put", "delete"]:
            return {"data": json.dumps(data, sort_keys=True)}
        return {}

    def _setup_authentication(self, kwargs):
        authentication_schemes = {
            "basic": self._setup_basic_authentication,
            "token": self._setup_token_authentication,
            "installation": self._setup_installation_authentication,
            "app": self._setup_app_authentication,
        }
        if kwargs.get("auth"):
            authentication_schemes.get(kwargs.get("auth"))(kwargs)

    def _setup_basic_authentication(self, kwargs):
        assert kwargs["username"]
        assert kwargs["password"]
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.auth = kwargs["auth"]

    def _setup_token_authentication(self, kwargs):
        assert kwargs["token"]
        self.token = kwargs["token"]
        self.auth = kwargs["auth"]

    def _setup_installation_authentication(self, kwargs):
        assert kwargs["app_id"]
        assert kwargs["private_key"]
        self.token, self.expires_at = self._app_auth_get_token(kwargs["app_id"], kwargs["private_key"])
        self.auth = kwargs["auth"]
        self.headers["accept"] = "application/vnd.github.machine-man-preview+json"

    def _setup_app_authentication(self, kwargs):
        assert kwargs["app_id"]
        assert kwargs["private_key"]
        self.jwt = self._app_auth_get_jwt(kwargs["app_id"], kwargs["private_key"])
        self.auth = kwargs["auth"]
        self.headers["accept"] = "application/vnd.github.machine-man-preview+json"

    def _app_auth_get_token(self, app_id, key):
        headers = {
            "Authorization": "Bearer {}".format(self._app_auth_get_jwt(app_id, key)),
            "Accept": "application/vnd.github.machine-man-preview+json",
        }
        installation_url = "{}/app/installations".format(self.base_url)
        installations = requests.get(installation_url, headers=headers).json()
        self.installation_id = [x.get("id") for x in installations if str(x.get("app_id")) == app_id].pop()
        installation_token_url = "{}/app/installations/{}/access_tokens".format(self.base_url, self.installation_id)
        response = requests.post(installation_token_url, headers=headers).json()
        return response["token"], response["expires_at"]

    def _app_auth_get_jwt(self, app_id, key):
        payload = {
            "iat": int(datetime.datetime.timestamp(datetime.datetime.now())),
            "exp": int(datetime.datetime.timestamp(datetime.datetime.now())) + (9 * 60),
            "iss": app_id,
        }
        return jwt.encode(payload, key, algorithm="RS256")

    def _auth(self, requests_kwargs):
        if getattr(self, "auth", None) == "basic":
            return {"auth": (self.username, self.password)}
        if getattr(self, "auth", None) in ["app", "token", "installation"]:
            _headers = {
                "app": {"Authorization": "Bearer {}".format(getattr(self, "jwt", None))},
                "token": {"Authorization": "token {}".format(getattr(self, "token", None))},
                "installation": {"Authorization": "token {}".format(getattr(self, "token", None))},
            }
            headers = requests_kwargs["headers"]
            headers.update(_headers.get(getattr(self, "auth", None)))
            return {"headers": headers}
        return {}

    def _get_parameters(self, definition, method):
        p = {}
        if definition.get("requestBody"):
            schema = copy.deepcopy(definition.get("requestBody")["content"]["application/json"]["schema"])
            if schema["type"] == "object":
                body_parameters = {}
                for k, v in schema["properties"].items():
                    v["in"] = "body"
                    v["required"] = k in schema.get("required", {})
                    body_parameters.update({k: v})
                p.update(body_parameters)
        p.update(utils.parameter_transform(definition.get("parameters")))
        return p
