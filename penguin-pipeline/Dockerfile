FROM python:3.8.11-slim-buster

RUN apt update
RUN apt install -y gcc g++ \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

COPY ./Pipfile /Pipfile

RUN pipenv install --system --skip-lock
