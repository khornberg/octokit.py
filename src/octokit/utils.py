import json
import os
import re


def snake_case(string):
    # From https://gist.github.com/jaytaylor/3660565#gistcomment-2271689
    return re.compile(r'(?!^)(?<!_)([A-Z])').sub(r'_\1', string).lower().replace(' ', '_').replace('-', '_')


def get_json_data(filename):
    with open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r') as f:
        return json.load(f)


def parameter_transform(params):
    return {param['name']: param for param in params}


def walk_path(obj, path):
    if len(path) == 1:
        assert path[0] in obj
    else:
        walk_path(obj[path[0]], path[1:])


def verify_path(obj, path):
    if not obj and len(path) == 1:
        return True
    if len(path) <= 2:
        return path[0] in obj
    if path[0] in obj:
        verify_path(obj[path[0]], path[1:])
    return False
