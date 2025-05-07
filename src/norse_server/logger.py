#!/usr/bin/env python
# logger.py

import os # noqa
import logging # noqa

logger = logging.getLogger()
logger.setLevel(os.getenv("NORSE_SERVER_LOGLEVEL", "INFO"))
