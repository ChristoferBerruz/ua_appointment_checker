FROM python:3.10-buster

RUN pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN touch README.md

# Install the project dependencies
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY ua_appointment_checker ./ua_appointment_checker

# Install the project itself (in case of poetry scripts)
RUN poetry install --without dev

ENTRYPOINT ["poetry", "run", "python", "-m", "ua_appointment_checker"]