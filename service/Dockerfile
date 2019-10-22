FROM python:3.7-slim as pipenv
LABEL image=pipenv
RUN pip install --no-cache-dir pipenv==2018.11.26

FROM pipenv as pipenv-deps
ENV PIPENV_VENV_IN_PROJECT=True
COPY Pipfile* /app/
WORKDIR /app
RUN pipenv sync

FROM pipenv-deps as builder
LABEL image=base
COPY setup.* /app/
COPY dajare /app/dajare/
COPY .coveragerc /app/
ENV prometheus_multiproc_dir /tmpmetrics
WORKDIR /app
RUN pipenv install -e . --skip-lock \
    && mkdir ${prometheus_multiproc_dir} \
    && chmod 777 ${prometheus_multiproc_dir}

FROM builder as test
LABEL image=test
COPY tests /app/tests
RUN pipenv sync --dev
RUN pipenv run pytest \
    && pipenv run pylint --rcfile setup.cfg dajare tests
    #&& pipenv run flake8 --teamcity dajare tests

FROM builder
MAINTAINER Lukas Schmid <lukas.m.schmid@gmail.com>

WORKDIR /app
COPY static/index.html /app/static/
COPY gunicorn_conf.py /app/
RUN adduser --system unicorn
USER unicorn
CMD rm -rf ${prometheus_multiproc_dir} && mkdir ${prometheus_multiproc_dir} && pipenv run gunicorn -c /app/gunicorn.conf --workers=5 --bind=0.0.0.0:5000 dajare:app



