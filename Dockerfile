FROM python:2.7

COPY requirements.txt .
RUN pip install -r requirements.txt
