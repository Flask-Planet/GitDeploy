# syntax=docker/dockerfile:1
FROM python:3.11-alpine
RUN apk add --update --no-cache gcc musl-dev linux-headers git supervisor
WORKDIR /autogit
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
#ENV AUTOGIT_GIT_URL='https://github.com/Flask-Planet/flask-planet.org.git'
#ENV AUTOGIT_GIT_PRIVATE=true
#ENV AUTOGIT_GIT_TOKEN_NAME=none
#ENV AUTOGIT_GIT_TOKEN=none
#ENV AUTOGIT_COMMAND='gunicorn -w 4 -b 0.0.0.0:5000 run:sgi'
#ENV AUTOGIT_WEBHOOK_ENABLED='true'
#ENV AUTOGIT_WEBHOOK_SK=33f00d646f273916552ca88bd57b80108f4bae404141f7f02f5b4160eee8730e5cc9717311f095d6aa1bb9465a5ec0d9fa980f2c5552d8ae77a2ed38a2f645b3
COPY . .
ENTRYPOINT ["python3", "main.py"]
