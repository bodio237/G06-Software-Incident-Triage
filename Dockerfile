FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY src ./src
COPY scenarios ./scenarios
COPY ui ./ui

RUN pip install --no-cache-dir --no-deps -e .

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "ticket_app.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]