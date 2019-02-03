FROM python:3.6-alpine3.6

ENV DJANGO_ENV production

ADD . /eoj
WORKDIR /eoj

HEALTHCHECK --interval=5s --retries=3 CMD python2 /eoj/deploy/health_check.py

RUN apk add --update --no-cache build-base nginx openssl curl unzip supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev && \
    pip install --no-cache-dir -r /eoj/deploy/requirements.txt && \
    apk del build-base --purge
