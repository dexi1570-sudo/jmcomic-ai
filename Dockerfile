FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE CHANGELOG.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

CMD ["sh","-c","exec jmai mcp http --host 0.0.0.0 --port \"${PORT:-8000}\""]
