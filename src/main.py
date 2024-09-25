#!/usr/bin/env python

"""\
This script runs server instance for Norse
"""

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import norse
import torch

from .helpers import get_arguments, do_exec
from .utils import ErrorHandler


app = Flask(__name__)
CORS(app)


@app.errorhandler(ErrorHandler)
def error_handler(e):
    return jsonify(e.to_dict()), e.status_code


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
