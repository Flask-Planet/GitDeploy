# syntax=docker/dockerfile:1
FROM python:3.11-alpine
WORKDIR /autogit
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "AutoGit.py"]
