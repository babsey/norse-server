#!/usr/bin/env python
# utils.py

import os
import sys
import traceback


class ErrorHandler(Exception):
    status_code = 400
    lineno = -1

    def __init__(self, message, lineno=None, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if lineno is not None:
            self.lineno = lineno
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        if self.lineno != -1:
            rv["lineNumber"] = self.lineno
        return rv


def get_boolean_environ(env_key, default_value="false"):
    env_value = os.environ.get(env_key, default_value)
    return env_value.lower() in ["yes", "true", "t", "1"]


def get_lineno(err, tb_idx):
    lineno = -1
    if hasattr(err, "lineno") and err.lineno is not None:
        lineno = err.lineno
    else:
        tb = sys.exc_info()[2]
        # if hasattr(tb, "tb_lineno") and tb.tb_lineno is not None:
        #     lineno = tb.tb_lineno
        # else:
        lineno = traceback.extract_tb(tb)[tb_idx][1]
    return lineno


def get_or_error(func):
    """Wrapper to exec function."""

    def func_wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)

        except (KeyError, SyntaxError, TypeError, ValueError) as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            lineno = get_lineno(err, 1)

        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            lineno = get_lineno(err, -1)

        for line in traceback.format_exception(*sys.exc_info()):
            print(line, flush=True)

        if lineno == -1:
            message = "%s: %s" % (error_class, detail)
        else:
            message = "%s at line %d: %s" % (error_class, lineno, detail)
        raise ErrorHandler(message, lineno)

    return func_wrapper
