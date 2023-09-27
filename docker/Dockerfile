FROM quay.io/norse/norse:v1.0

COPY . /norse-server

WORKDIR /norse-server

RUN pip install /norse-server

COPY ./docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 11428
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]