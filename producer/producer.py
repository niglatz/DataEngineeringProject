import time
import json
import csv
from confluent_kafka import Producer
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='producer.log',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create Kafka Producer instance
p = Producer({'bootstrap.servers': 'kafka1:9092'})
print('Kafka Producer has been initiated...')

# Callback function to handle produced message acknowledgment
def receipt(err, msg):
    if err is not None:
        print('Error: {}'.format(err))
    else:
        # Log successful message production
        message = 'Produced message on topic {} with value of {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)

# Main function to read CSV files and produce messages to Kafka topic
def main():
    for i in range(19):
        with open("alltrips_{}.csv".format(i), "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                # Print the row for debugging
                print(row)
                # Convert row to JSON and produce to Kafka topic
                m = json.dumps(row)
                p.produce('bike_rides', m.encode('utf-8'), callback=receipt)
                # Poll for events, set to 0 for non-blocking
                p.poll(0)
                # Introduce sleep to control message production rate
                time.sleep(0.01)

    # Ensure all messages are sent before closing
    p.flush()

if __name__ == '__main__':
    main()
