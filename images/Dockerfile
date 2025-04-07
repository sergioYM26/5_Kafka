FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y curl unzip vim iputils-ping && \
    rm -rf /var/lib/apt/lists/*

RUN pip install kafka-python==2.1.5 'transformers[torch]==4.51.0' pandas==2.2.3

COPY data /app/data
COPY src /app/src

WORKDIR /app

ENV RUNTIME="docker"


ENTRYPOINT ["/bin/bash", "-c", "sleep 86400"]
