import copy
import re
from collections import defaultdict

import requests
from octokit_routes import specifications

from octokit import utils
from octokit.base import Base

page_regex = re.compile(r'[\?\&]page=(\d+)[_&=%+\w\d]*>; rel="(\w+)"')


class Octokit(Base):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._create(specifications[kwargs.get("routes", "api.github.com")])
        self._setup_authentication(kwargs)

    def _create(self, definitions):
        classes = self._create_classes(definitions)
        bases = [object]
        for cls_name, class_attributes in classes.items():
            cls = type(cls_name, tuple(bases), class_attributes)
            setattr(self, cls_name, cls)

    def _create_classes(self, definitions):
        class_attributes = defaultdict(dict)
        for path, path_object in definitions["paths"].items():
            for method, method_object in path_object.items():
                cls_name, methods = self._get_class_methods(method_object, method, path)
                class_attributes[cls_name].update(methods)
        return class_attributes

    def _create_method(self, name, definition, method, path):
        def _api_call(*args, **kwargs):
            method_headers = kwargs.pop("headers") if kwargs.get("headers") else {}
            self.validate(kwargs, definition)
            requests_kwargs = {"headers": self._get_headers(method_headers)}
            parameter_map = self._get_parameters(definition, method)
            url, data_kwargs = self._form_url(kwargs, path, parameter_map)
            requests_kwargs.update(self._data(data_kwargs, parameter_map, method))
            requests_kwargs.update(self._auth(requests_kwargs))
            _response = getattr(requests, method)(url, **requests_kwargs)
            try:
                attributes = _response.json()
            except ValueError:
                attributes = _response.text
            new_self = copy.deepcopy(self)
            setattr(new_self, "_response", _response)
            setattr(new_self, "json", attributes)
            setattr(new_self, "response", new_self._convert_to_object(attributes))
            return new_self

        _api_call.__name__ = name
        _api_call.__doc__ = definition["description"]
        return _api_call

    def _get_names_from_operation_id(self, _object):
        _cls_name, _id_name = _object.get("operationId").split("/")
        cls_name = utils.snake_case(str(_cls_name))
        method_id_name = utils.snake_case(str(_id_name))
        return cls_name, method_id_name

    def _get_deprecated_methods(self, methods, method_object):
        deprecated_methods = {}
        if method_object.get("x-changes"):
            for change in method_object["x-changes"]:
                if change.get("type") == "operation":
                    before_cls, before_name = self._get_names_from_operation_id(change.get("before"))
                    after_cls, after_name = self._get_names_from_operation_id(change.get("after"))
                    if before_cls == after_cls and methods.get(after_name):
                        deprecated_methods.update({before_name: methods[after_name]})
        return deprecated_methods

    def _get_class_methods(self, method_object, method, path):
        cls_name, method_id_name = self._get_names_from_operation_id(method_object)
        method_name = utils.snake_case(str(method_object.get("summary")))
        methods = {
            method_id_name: self._create_method(method_id_name, method_object, method, path),
            method_name: self._create_method(method_name, method_object, method, path),
        }
        methods.update(self._get_deprecated_methods(methods, method_object))
        return cls_name, methods

    def _convert_to_object(self, item):
        if isinstance(item, dict):
            return type("ResponseData", (object,), {k: self._convert_to_object(v) for k, v in item.items()})
        if isinstance(item, list):
            return list((self._convert_to_object(value) for index, value in enumerate(item)))
        else:
            return item

    def set_pages(self, obj, previous_page_requested=None):
        response_headers = obj._response.headers
        links = response_headers.get("Link", None)
        if links:
            matches = re.findall(page_regex, links)
            if matches:
                for page, kind in matches:
                    setattr(obj, "{}_page".format(kind), int(page))
                setattr(obj, "pages", getattr(obj, "last_page", previous_page_requested))
                setattr(obj, "has_pages", True)
                setattr(obj, "current_page", previous_page_requested or getattr(obj, "next_page") - 1)
                setattr(obj, "is_last_page", obj.pages == obj.current_page)
            else:
                setattr(obj, "has_pages", False)
        return obj

    def paginate(self, obj, page=1, **kwargs):
        response = self.set_pages(obj(page=page, **kwargs))
        yield response.json
        if hasattr(response, "is_last_page"):
            while not response.is_last_page:
                response = self.set_pages(obj(page=response.next_page, **kwargs), response.next_page)
                yield response.json
