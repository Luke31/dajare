FROM python:3.7-slim as pipenv
LABEL image=pipenv
RUN pip install --no-cache-dir pipenv==2018.11.26

FROM pipenv as pipenv-deps
ENV PIPENV_VENV_IN_PROJECT=True
RUN apt-get update && apt-get install -y curl build-essential \
 && curl http://www.phontron.com/kytea/download/kytea-0.4.7.tar.gz --output kytea.tar.gz \
 && tar -xvf kytea.tar.gz \
 && cd kytea-0.4.7 \
 && ./configure \
 && make \
 && make install \
 && cd .. && rm kytea.tar.gz && rm -r kytea-0.4.7
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

#FROM builder as model
#LABEL image=model
#WORKDIR /app/
#COPY dajare/emotionpredictor.py /app/
#COPY dajare/loadmodel.py /app/
#RUN pipenv run python loadmodel.py

FROM builder as test
LABEL image=test
#COPY --from=model /app/emotionpredictor.pkl .
COPY tests /app/tests
RUN pipenv sync --dev
COPY elookup.pkl /app/.
RUN pipenv run pytest \
    && pipenv run pylint --rcfile setup.cfg dajare tests \
    && pipenv run flake8 --teamcity dajare tests

FROM builder
MAINTAINER Lukas Schmid <lukas.m.schmid@gmail.com>
WORKDIR /app
#COPY --from=model /app/emotionpredictor.pkl .
COPY elookup.pkl .
COPY static/index.html /app/static/
COPY gunicorn_conf.py /app/
RUN adduser --system unicorn
USER unicorn
CMD rm -rf ${prometheus_multiproc_dir} && mkdir ${prometheus_multiproc_dir} && pipenv run gunicorn -c /app/gunicorn.conf --workers=5 --bind=0.0.0.0:5000 dajare:app



