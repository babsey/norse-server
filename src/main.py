#!/usr/bin/env python

"""
This script runs server instance for Norse.
"""

import logging

from flask import Flask, jsonify, request
from flask.logging import default_handler
from flask_cors import CORS

import norse
import torch

from .helpers import do_exec
from .utils import ErrorHandler, get_arguments


# This ensures that the logging information shows up in the console running the server,
# even when Flask's event loop is running.
# https://flask.palletsprojects.com/en/2.3.x/logging/
root = logging.getLogger()
root.addHandler(default_handler)


app = Flask(__name__)
CORS(app)


# https://flask.palletsprojects.com/en/2.3.x/errorhandling/
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
def route_exec():
    """Route to execute script in Python."""

    kwargs = get_arguments(request)
    response = do_exec(kwargs)
    return jsonify(response)
