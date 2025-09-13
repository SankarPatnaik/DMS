FROM python:3.11-slim
WORKDIR /app
COPY libs /app/libs
COPY apps/gateway /app/apps/gateway
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV PYTHONPATH=/app
CMD ["uvicorn", "apps.gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
