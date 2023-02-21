# xfoil-python only seems to work on python 3.6.
FROM python:3.10-slim-buster

# Allow statements and log messages to immediately appear in the Knative logs on Google Cloud.
ENV PYTHONUNBUFFERED True

ENV PROJECT_ROOT=/workspace
WORKDIR $PROJECT_ROOT

RUN apt-get update -y  \
    && apt-get install -y --fix-missing build-essential gfortran git curl  \
    && rm -rf /var/lib/apt/lists/*

# Install poetry.
ENV POETRY_HOME=/root/.poetry
ENV PATH "$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - && poetry config virtualenvs.create false;

COPY pyproject.toml poetry.lock

# Install dependencies but not the local package.
RUN if [ -f "pyproject.toml" ]; then poetry install  \
    --no-ansi  \
    --no-interaction  \
    --no-cache  \
    --no-root  \
    --only main;  \
    fi

# Copy local code to the application root directory.
COPY . .

# Install local package.
RUN poetry install --only main

EXPOSE $PORT

ENV USE_OCTUE_LOG_HANDLER=1
ENV COMPUTE_PROVIDER=GOOGLE_CLOUD_RUN

ARG GUNICORN_WORKERS=1
ENV GUNICORN_WORKERS=$GUNICORN_WORKERS

ARG GUNICORN_THREADS=8
ENV GUNICORN_THREADS=$GUNICORN_THREADS

# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers $GUNICORN_WORKERS --threads $GUNICORN_THREADS --timeout 0 octue.cloud.deployment.google.cloud_run.flask_app:app
