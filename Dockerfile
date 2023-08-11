FROM python:3.10-alpine

adjust here
ENV DB_CONNECT="postgresql+asyncpg://edupalai:edupalai@edupalai-db/edupalai"

RUN apk update && apk add postgresql-dev python3-dev gcc musl-dev linux-headers libc-dev g++

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

WORKDIR /app
CMD ["manage.py", "runserver", "0.0.0.0:80"]
