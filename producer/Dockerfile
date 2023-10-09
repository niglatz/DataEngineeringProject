FROM python:3.7.12

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install confluent-kafka

WORKDIR /usr/app/src

COPY producer.py ./
COPY alltrips_*.csv ./

CMD [ "python", "-u", "./producer.py"]
