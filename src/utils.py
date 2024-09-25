#!/usr/bin/env python
# utils.py

import os
import sys
import traceback


# https://flask.palletsprojects.com/en/2.3.x/errorhandling/
class ErrorHandler(Exception):
    status_code = 400
    line_number = -1

    def __init__(self, message, line_number=None, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if line_number is not None:
            self.line_number = line_number
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        if self.line_number != -1:
            rv["lineNumber"] = self.line_number
        return rv


def get_boolean_environ(env_key, default_value="false"):
    env_value = os.environ.get(env_key, default_value)
    return env_value.lower() in ["yes", "true", "t", "1"]


def get_line_number(err, tb_idx):
    if hasattr(err, "lineno") and err.lineno is not None:
        return err.lineno
    else:
        tb = sys.exc_info()[2]
        return traceback.extract_tb(tb)[tb_idx][1]


def get_or_error(func):
    """Wrapper to exec function."""

    def func_wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)

        except (KeyError, SyntaxError, TypeError, ValueError) as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            line_number = get_line_number(err, 1)

        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            line_number = get_line_number(err, -1)

            for line in traceback.format_exception(*sys.exc_info()):
                print(line, flush=True)

        if line_number is not None:
            message = "%s at line %d: %s" % (error_class, line_number, detail)
        else:
            message = "%s: %s" % (error_class, detail)
            line_number = -1
        raise ErrorHandler(message, line_number)

    return func_wrapper
