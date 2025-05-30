FROM python:3.12
ENV PYTHONUNBUFFERED=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_HOME=/opt/poetry \
  PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY . /app/
RUN $POETRY_HOME/bin/poetry config virtualenvs.create false \
 && $POETRY_HOME/bin/poetry install --no-root --no-interaction --no-ansi $(test "$IS_CI" = "True" && echo "--no-dev")

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
