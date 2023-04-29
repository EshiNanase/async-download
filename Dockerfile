FROM python:3.8.14-alpine3.16

ENV PYTHONUNBUFFERED 1

COPY ./app /app
WORKDIR /app

COPY ./requirements.txt /tmp/requirements.txt
RUN apk add --no-cache zip && \
    python -m venv venv && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /tmp \

EXPOSE 80
