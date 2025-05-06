#!/usr/bin/env python
# logger.py

import os # noqa
import logging # noqa
from flask.logging import default_handler # noqa

logger = logging.getLogger()
logger.addHandler(default_handler)
logger.setLevel(os.getenv("NORSE_SERVER_LOGLEVEL", "INFO"))
