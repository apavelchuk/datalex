FROM python:3.11-alpine

RUN apk update && apk add postgresql-dev python3-dev gcc musl-dev linux-headers libc-dev g++ bash

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app/

WORKDIR /app
EXPOSE 8000

# Download and make wait-for-it.sh executable
RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -O /usr/local/bin/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

CMD sh -c "wait-for-it.sh datalex-db:5432 -- ./manage.py migrate && ./manage.py collectstatic && ./manage.py runserver 0.0.0.0:8000"
