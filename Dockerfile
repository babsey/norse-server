FROM quay.io/norse/norse:v1.0

COPY . /norse-server

WORKDIR /norse-server

RUN pip install /norse-server

ENTRYPOINT gunicorn -b 0.0.0.0:11428 norse_server.server:app