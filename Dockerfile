FROM python:3.12.4-bullseye

ENV POETRY_VERSION=1.8.3 POETRY_HOME=/poetry
ENV PATH=/poetry/bin:$PATH
RUN curl -sSL https://install.python-poetry.org | python3 -
WORKDIR /palm
COPY api api
COPY enums enums
COPY schemas schemas
COPY responses responses
COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --only main
COPY bin/start-api bin/start
CMD bin/start
