FROM python:3.12-slim

WORKDIR /workspace

COPY pyproject.toml README.md ./
COPY app ./app
COPY agents ./agents
COPY db ./db
COPY data ./data
COPY evals ./evals
COPY local_semantic ./local_semantic

RUN pip install --no-cache-dir -e .
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /workspace/data/raw /workspace/data/processed \
    && chown -R appuser:appuser /workspace

EXPOSE 8000

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=3)"]

CMD ["sh", "-c", "python -m app.bootstrap && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
