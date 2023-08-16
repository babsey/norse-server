
import sys
import re

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from werkzeug.exceptions import abort
from werkzeug.wrappers import Response

import numpy as np
import torch
import norse

import RestrictedPython
import time

import traceback

from copy import deepcopy

import os

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "norse": norse.__version__,
            "torch": torch.__version__,
        }
    )

@app.route("/exec", methods=["GET", "POST"])
@cross_origin()
def route_exec():
    """Route to execute script in Python."""

    kwargs = get_arguments(request)
    response = do_exec(kwargs)
    return jsonify(response)



def get_arguments(request):
    """Get arguments from the request."""
    kwargs = {}
    if request.is_json:
        json = request.get_json()
        if isinstance(json, dict):
            kwargs = json
        #else: TODO: Error

    elif len(request.form) > 0:
        kwargs = request.form.to_dict()
    elif len(request.args) > 0:
        kwargs = request.args.to_dict()
    return kwargs


def do_exec(kwargs):
    try:
        source_code = kwargs.get("source", "")
        source_cleaned = clean_code(source_code)

        locals_ = dict()
        response = dict()
        code = RestrictedPython.compile_restricted(source_cleaned, "<inline>", "exec")  # noqa
        globals_ = get_restricted_globals()
        # globals_.update(get_modules_from_env())
        globals_.update({
            "norse": norse,
            "nt": norse.torch,
            "torch": torch,
            "np": np,
            "numpy": np,
        })
        exec(code, globals_, locals_)
        
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

    except Exception as e:
        for line in traceback.format_exception(*sys.exc_info()):
            print(line, flush=True)
        abort(Response(str(e), 400))

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
        raise ValueError(f"Cannot serialize data of type {type(data)}")


def clean_code(source):
    codes = re.split(r"\n+|;", source)
    codes = [code.strip() for code in codes]
    code_cleaned = filter(lambda code: not (code.startswith("import ") or code.startswith("from ")), codes)  # noqa
    return "\n".join(code_cleaned)
    

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