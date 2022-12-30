# syntax=docker/dockerfile:1
FROM python:3.11-alpine
RUN mkdir -p /autogit/logs
RUN mkdir -p /autogit/config
RUN mkdir -p /autogit/repo
RUN apk add --update --no-cache gcc musl-dev linux-headers git supervisor openrc
ADD supervisord.conf /etc/
WORKDIR /autogit
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["supervisord", "--nodaemon", "--configuration", "/etc/supervisord.conf"]
