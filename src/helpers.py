#!/usr/bin/env python
# helpers.py

import time

import torch
import numpy as np
import RestrictedPython

from .utils import Capturing, clean_code, get_boolean_environ, get_modules_from_env, get_or_error


RESTRICTION_DISABLED = get_boolean_environ("NORSE_SERVER_DISABLE_RESTRICTION")
EXCEPTION_ERROR_STATUS = 400

if RESTRICTION_DISABLED:
    msg = "Norse Server runs without a RestrictedPython trusted environment."
    print(f"***\n*** WARNING: {msg}\n***")


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
