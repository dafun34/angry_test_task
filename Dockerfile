FROM python:3.11-slim

RUN apt-get -qq update && apt install wait-for-it

WORKDIR /app



COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app/

ENV PYTHONPATH=/app

CMD ["bash",  "start.sh"]