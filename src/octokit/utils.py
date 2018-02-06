import re


def snake_case(string):
    """
        From https://gist.github.com/jaytaylor/3660565#gistcomment-2271689
    """
    return re.compile(r'(?!^)(?<!_)([A-Z])').sub(r'_\1', string).lower()
