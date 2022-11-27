FROM python:3.10.7-alpine

WORKDIR ./bot

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 4444
