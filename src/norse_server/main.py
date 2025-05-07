#!/usr/bin/env python
# main.py

"""
This script runs server instance for Norse.
"""

from fastapi import FastAPI, Request, status # noqa
from fastapi.encoders import jsonable_encoder # noqa
from fastapi.responses import JSONResponse # noqa
from fastapi.middleware.cors import CORSMiddleware # noqa
from pydantic import BaseModel # noqa

import uvicorn # noqa

import norse # noqa
import torch # noqa

from .exceptions import ErrorHandler
from .helpers import do_exec
from .logger import logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# https://fastapi.tiangolo.com/tutorial/handling-errors/?h=erro#use-the-requestvalidationerror-body
@app.exception_handler(ErrorHandler)
async def validation_exception_handler(request: Request, exc: ErrorHandler):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(exc.to_dict()),
    )


@app.get("/")
def index():
    logger.debug("Index route")

    return {
        "norse": norse.__version__,
        "torch": torch.__version__,
    }


class Data(BaseModel):
    response_keys: str | list = "response"
    source: str = ""


@app.post("/exec")
def route_exec(data: Data):
    """Route to execute script in Python."""
    logger.debug("Route to exec script")

    response = do_exec(data)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=11428)
