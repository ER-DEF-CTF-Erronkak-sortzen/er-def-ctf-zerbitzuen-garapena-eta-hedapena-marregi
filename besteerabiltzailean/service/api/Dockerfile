#
FROM python:3.12-slim

#
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

#
RUN pip install --no-cache-dir -r requirements.txt

#
COPY ./main.py .
COPY ./app ./app

