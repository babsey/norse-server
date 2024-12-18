#!/usr/bin/env python
# main.py

"""
This script runs server instance for Norse.
"""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import uvicorn

import norse
import torch

from .exceptions import ErrorHandler
from .helpers import do_exec

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

    response = do_exec(data)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=11428, log_config=f"norse-server-log.ini")
