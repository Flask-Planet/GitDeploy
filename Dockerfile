# syntax=docker/dockerfile:1
FROM python:3.11-alpine
RUN apk add --update --no-cache gcc musl-dev linux-headers git supervisor openrc
WORKDIR /autogit
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python3", "main.py"]
