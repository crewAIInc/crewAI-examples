FROM python:3.12-slim

RUN apt-get update && apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root
COPY . .
RUN poetry install
COPY <<EOF /entrypoint.sh
#!/bin/sh
set -e
if test -z \${OPENAI_API_KEY}; then
    echo "OPENAI_API_KEY is not set, using Docker Model Runner \${MODEL_RUNNER_URL}"
    export OPENAI_BASE_URL=\${MODEL_RUNNER_URL}
    export OPENAI_MODEL_NAME=openai/\${MODEL_RUNNER_MODEL}
    export OPENAI_API_KEY=does_not_matter_but_cannot_be_empty
fi
exec poetry run marketing_posts
EOF
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
