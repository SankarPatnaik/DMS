FROM python:3.11-slim
WORKDIR /app
COPY libs /app/libs
COPY apps/dms /app/apps/dms
COPY database /app/database
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV PYTHONPATH=/app
WORKDIR /app/apps/dms
CMD ["bash","-lc","alembic upgrade head && uvicorn apps.dms.main:app --host 0.0.0.0 --port ${UVICORN_PORT:-8081}"]
