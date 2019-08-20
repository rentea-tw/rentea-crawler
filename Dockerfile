FROM python:3.7
WORKDIR /app

COPY ./requirements.txt /app

# Quick hack for Ubuntu DNS issue
# source: https://github.com/docker/docker.github.io/issues/3131
RUN echo nameserver 101.101.101.101 >> /etc/resolv.conf && pip install -r requirements.txt

