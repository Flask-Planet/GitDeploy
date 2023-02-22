# syntax=docker/dockerfile:1
FROM python:3.11-alpine
RUN apk add --update --no-cache gcc musl-dev linux-headers git supervisor
WORKDIR /autogit
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
#ENV GD_GIT_URL='https://github.com/Flask-Planet/flask-planet.org.git'
#ENV GD_GIT_PRIVATE=true
#ENV GD_GIT_TOKEN_NAME=none
#ENV GD_GIT_TOKEN=none
#ENV GD_COMMAND='gunicorn -w 3 -b 0.0.0.0:5000 run:sgi'
#ENV GD_WEBHOOK_ENABLED='true'
#ENV GD_WEBHOOK_SK=SuperSecretKey
COPY . .
RUN mkdir "instance"
ENTRYPOINT ["python3", "start.py"]
