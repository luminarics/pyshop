FROM python:3.13-bookworm

ARG POETRY_VERSION=1.8.2
ARG GIT_SHA=unknown
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GIT_SHA=$GIT_SHA

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --only main

COPY . /app

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
