FROM python:3-alpine

WORKDIR /app
COPY requirements.txt /app
RUN apk add --virtual=.build-deps --no-cache build-base postgresql-dev libffi-dev musl-dev openssl-dev && \
    apk add --virtual=.run-deps --no-cache libpq && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps
COPY . /app

CMD ["errbot"]

LABEL maintainer="Simone Esposito <chaufnet@gmail.com>"
