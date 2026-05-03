FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY server ./server
COPY sdk ./sdk
COPY templates ./templates

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
