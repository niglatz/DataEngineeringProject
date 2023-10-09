FROM python:3.7.12

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install confluent-kafka
RUN pip3 install pymongo

WORKDIR /usr/app/src

COPY consumer.py ./

CMD [ "python", "-u",  "./consumer.py"]
