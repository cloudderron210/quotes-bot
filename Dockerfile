FROM python:3.12-alpine as base

ARG DEV=true

ENV VIRTUAL_ENV=/app/.venv/ \
  PATH="/app/.venv/bin:${PATH}"

RUN apk update && \
  apk add libpq

FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apk update && \
  apk add musl-dev build-base gcc gfortran openblas-dev

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.1.1


COPY pyproject.toml poetry.lock ./
RUN if [ $DEV ]; then \
  poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR; \
  else \
  poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR; \
  fi



FROM base as runtime 

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . .


RUN chmod +x /start.sh

# ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
ENTRYPOINT ["/start.sh"]



