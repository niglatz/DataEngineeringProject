import datetime
import json
import time

from datetime import datetime, timedelta
import pymongo
from confluent_kafka import Consumer

# Initialize Kafka consumer
c = Consumer({'bootstrap.servers': 'kafka1:9092', 'group.id': 'python-consumer', 'auto.offset.reset': 'earliest'})
print('Kafka Consumer has been initiated...')

# Subscribe to the 'bike_rides' topic
print('Available topics to consume: ', c.list_topics().topics)
c.subscribe(['bike_rides'])
myclient = pymongo.MongoClient("mongodb://root:example@mongo1:27017")
current_date = datetime.strptime('2020-05-01', "%Y-%m-%d")
weekday_counter = 1


def init_mongo_db():
    """
    Initialize MongoDB collections for daily and weekly jobs.
    """
    global jobs_daily
    jobs_db = myclient["Jobs"]
    jobs_daily = jobs_db["daily"]
    jobs_weekly = jobs_db["weekly"]
    jobs_daily.drop()
    job = {"type": "daily",
           "weekday": 1,
           "date": datetime.now()}
    jobs_daily.insert_one(job)
    jobs_daily.delete_one(job)
    weekly = {"week": 1,
              "bike_date_first_day": datetime.now(),
              "bike_date_last_day": datetime.now()}
    jobs_weekly.insert_one(weekly)
    jobs_weekly.delete_one(weekly)


# Initialize MongoDB collections
init_mongo_db()


def main():
    """
    Main function to consume Kadsafka messages and update MongoDB collections.
    """
    global current_date, weekday_counter
    bike_data_db = myclient["BikeData"]
    bike_ride_collection = bike_data_db["BikeRides"]
    bike_ride_collection.drop()

    while True:
        msg = c.poll(1.0)  # timeout
        if msg is None:
            continue
        if msg.error():
            print('Error: {}'.format(msg.error()))
            continue
        data = msg.value().decode()
        bike_ride = json.loads(data)
        date = datetime.strptime(bike_ride['date'], "%Y-%m-%d")
        value = {
            "ride_id": int(bike_ride['ride_id']),
            "rideable_type": bike_ride['rideable_type'],
            "started_at": datetime.strptime(bike_ride['started_at'], "%Y-%m-%d %H:%M:%S"),
            "ended_at": datetime.strptime(bike_ride['ended_at'], "%Y-%m-%d %H:%M:%S"),
            "member_casual": bike_ride['member_casual'],
            "date": date,
            "day_of_week": bike_ride['day_of_week'],
            "ride_length": float(bike_ride['ride_length'])}

        if current_date < date:
            print("#######Create Daily Job#######")
            job = {"type": "daily",
                   "weekday": weekday_counter,
                   "date": current_date}
            print(job)
            print(weekday_counter)
            jobs_daily.insert_one(job)
            current_date = current_date + timedelta(days=1)
            if weekday_counter == 7:
                weekday_counter = 1
            else:
                weekday_counter = weekday_counter + 1

        bike_ride_collection.insert_one(value)

    c.close()


if __name__ == '__main__':
    # Initial delay before starting main function. So that the Mongodb ReplicaSet is initialized
    time.sleep(30)
    # Initialize MongoDB collections
    init_mongo_db()
    # Start main function
    main()
