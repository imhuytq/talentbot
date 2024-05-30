FROM python:3.11-bookworm as builder

RUN apt-get update && apt-get install -y \
    libpq-dev libgl-dev poppler-utils tesseract-ocr libreoffice

RUN pip install poetry==1.7.1
RUN poetry config virtualenvs.create false

ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
COPY pyproject.toml poetry.lock* ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --no-interaction --no-ansi --no-root --no-directory --without test --without lint

FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 libgl1 poppler-utils tesseract-ocr libreoffice \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

WORKDIR /app
COPY . ./

ENV STREAMLIT_SERVER_PORT=8501

CMD ["python", "-m", "streamlit", "run", "talentbot/main.py", "--server.address=0.0.0.0"]
