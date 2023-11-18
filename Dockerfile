FROM python:3.10-alpine

WORKDIR /opt/app/api

COPY requirements.txt requirements.txt
COPY ./src/main.py .

RUN  pip install -r requirements.txt --no-cache-dir

COPY ./src ./src

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
