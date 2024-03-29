#dev
FROM python:3.11.5 AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING='utf-8'

WORKDIR /app

COPY requirements* ./

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements-dev.txt

COPY . .
COPY ./src/main.py .

RUN apt-get update && apt-get install -y gettext=0.21-12 --no-install-recommends && \
    apt-get clean  && rm -rf /var/lib/apt/lists/* && \
    useradd -d /app -s /bin/bash app && \
    chown -R app /app && \
    chgrp -R 0 /app && \
    chmod -R g=u /app

USER app

EXPOSE 8000

CMD ["tail", "-f", "/dev/null"]

#prod
FROM dev AS prod

ENTRYPOINT ["/app/docker-entrypoint.sh"]