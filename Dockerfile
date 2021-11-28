FROM python:3.10

WORKDIR /code
COPY requirements.txt /srv/tmp/
RUN pip install -r /srv/tmp/requirements.txt

