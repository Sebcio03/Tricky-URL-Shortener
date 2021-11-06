FROM python:3.9

RUN apt update -y && apt upgrade -y
RUN PYTHONUNBUFFERED=1
RUN pip install --upgrade pip setuptools

COPY requirements.txt .
RUN pip install --requirement requirements.txt

WORKDIR /project/