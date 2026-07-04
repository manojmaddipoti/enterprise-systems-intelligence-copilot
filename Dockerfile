FROM python:3.12-slim

WORKDIR /workspace

COPY pyproject.toml README.md ./
COPY app ./app
COPY agents ./agents
COPY db ./db
COPY data ./data
COPY evals ./evals

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
