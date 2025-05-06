#!/usr/bin/env python
# utils.py

import ast # noqa
import importlib # noqa
import io # noqa
import os # noqa
import re # noqa
import sys # noqa

MODULES = os.environ.get(
    "NORSE_SERVER_MODULES",
    ";".join(["import norse", "import torch", "import numpy as np"]),
)


class Capturing(list):
    """Monitor stdout contents i.e. print."""

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def clean_code(source):
    codes = re.split("\n|; ", source)
    codes_cleaned = []  # noqa
    for code in codes:
        if code.startswith("import") or code.startswith("from"):
            codes_cleaned.append("#" + code)
        else:
            codes_cleaned.append(code)
    return "\n".join(codes_cleaned)


# def get_arguments(request):
#     """Get arguments from the request."""
#     kwargs = {}
#     if request.is_json:
#         json = request.get_json()
#         if isinstance(json, dict):
#             kwargs = json
#         # else: TODO: Error

#     elif len(request.form) > 0:
#         kwargs = request.form.to_dict()
#     elif len(request.args) > 0:
#         kwargs = request.args.to_dict()
#     return kwargs


def get_boolean_environ(env_key, default_value="false"):
    env_value = os.environ.get(env_key, default_value)
    return env_value.lower() in ["yes", "true", "t", "1"]


def get_modules_from_env():
    """Get modules from environment variable NORSE_SERVER_MODULES.

    This function converts the content of the environment variable NORSE_SERVER_MODULES:
    to a formatted dictionary for updating the Python `globals`.

    Here is an example:
        `NORSE_SERVER_MODULES="import norse; import numpy as np; from numpy import random"`
    is converted to the following dictionary:
        `{'norse': <module 'norse'> 'np': <module 'numpy'>, 'random': <module 'numpy.random'>}`
    """
    modules = {}
    try:
        parsed = ast.iter_child_nodes(ast.parse(MODULES))
    except (SyntaxError, ValueError):
        raise SyntaxError(
            "The Norse server module environment variables contains syntax errors."
        )
    for node in parsed:
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules[alias.asname or alias.name] = importlib.import_module(
                    alias.name
                )
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                modules[alias.asname or alias.name] = importlib.import_module(
                    f"{node.module}.{alias.name}"
                )
    return modules
