#!/usr/bin/env python
# helpers.py

import ast
import importlib
import os
import sys

import io

import torch
import numpy as np

import RestrictedPython
import time

from .utils import get_boolean_environ, get_or_error


MODULES = os.environ.get("NORSE_SERVER_MODULES", "import norse; import torch; import numpy as np")
RESTRICTION_DISABLED = get_boolean_environ("NORSE_SERVER_DISABLE_RESTRICTION")
EXCEPTION_ERROR_STATUS = 400

if RESTRICTION_DISABLED:
    msg = "Norse Server runs without a RestrictedPython trusted environment."
    print(f"***\n*** WARNING: {msg}\n***")


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


def get_arguments(request):
    """Get arguments from the request."""
    kwargs = {}
    if request.is_json:
        json = request.get_json()
        if isinstance(json, dict):
            kwargs = json
        # else: TODO: Error

    elif len(request.form) > 0:
        kwargs = request.form.to_dict()
    elif len(request.args) > 0:
        kwargs = request.args.to_dict()
    return kwargs


def do_exec(kwargs):
    source_code = kwargs.get("source", "")
    source_cleaned = clean_code(source_code)

    locals_ = dict()
    response = dict()
    if RESTRICTION_DISABLED:
        with Capturing() as stdout:
            globals_ = globals().copy()
            globals_.update(get_modules_from_env())
            get_or_error(exec)(source_cleaned, globals_, locals_)
        if len(stdout) > 0:
            response["stdout"] = "\n".join(stdout)
    else:
        code = RestrictedPython.compile_restricted(source_cleaned, "<inline>", "exec")  # noqa
        globals_ = get_restricted_globals()
        globals_.update(get_modules_from_env())
        get_or_error(exec)(code, globals_, locals_)
        if "_print" in locals_:
            response["stdout"] = "".join(locals_["_print"].txt)

    if "return" in kwargs:
        if isinstance(kwargs["return"], list):
            data = dict()
            for variable in kwargs["return"]:
                data[variable] = locals_.get(variable, None)
        else:
            data = locals_.get(kwargs["return"], None)
        response["data"] = serialize_data(data)
    return response


def clean_code(source):
    codes = source.split("\n")
    codes_cleaned = []  # noqa
    for code in codes:
        if code.startswith("import") or code.startswith("from"):
            codes_cleaned.append("#" + code)
        else:
            codes_cleaned.append(code)
    return "\n".join(codes_cleaned)


def get_globals():
    """Get globals for exec function."""
    copied_globals = globals().copy()

    # Add modules to copied globals
    modlist = [(module, importlib.import_module(module)) for module in MODULES]
    modules = dict(modlist)
    copied_globals.update(modules)

    return copied_globals


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
        raise SyntaxError("The Norse server module environment variables contains syntax errors.")
    for node in parsed:
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules[alias.asname or alias.name] = importlib.import_module(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                modules[alias.asname or alias.name] = importlib.import_module(f"{node.module}.{alias.name}")
    return modules


def get_restricted_globals():
    """Get restricted globals for exec function."""

    def getitem(obj, index):
        typelist = (list, tuple, dict, torch.Tensor, np.ndarray)
        if obj is not None and type(obj) in typelist:
            return obj[index]
        msg = f"Error getting restricted globals: unidentified object '{obj}'."
        raise TypeError(msg)

    restricted_builtins = RestrictedPython.safe_builtins.copy()
    restricted_builtins.update(RestrictedPython.limited_builtins)
    restricted_builtins.update(RestrictedPython.utility_builtins)
    restricted_builtins.update(
        dict(
            max=max,
            min=min,
            sum=sum,
            time=time,
        )
    )

    restricted_globals = dict(
        __builtins__=restricted_builtins,
        _print_=RestrictedPython.PrintCollector,
        _getattr_=RestrictedPython.Guards.safer_getattr,
        _getitem_=getitem,
        _getiter_=iter,
        _unpack_sequence_=RestrictedPython.Guards.guarded_unpack_sequence,
        _write_=RestrictedPython.Guards.full_write_guard,
    )

    return restricted_globals


@get_or_error
def serialize_data(data):
    if isinstance(data, torch.Tensor):
        return data.detach().tolist()
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(v) for v in data]
    else:
        print(data)
        raise ValueError(f"Cannot serialize data of type {type(data)}")
