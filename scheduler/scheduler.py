import time
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import mean as _mean, col, round

import pymongo
import schedule

myclient = pymongo.MongoClient("mongodb://root:example@mongo1:27017")
jobs_db = myclient["Jobs"]
jobs_daily = jobs_db["daily"]
jobs_weekly = jobs_db["weekly"]


def job_daily_bike():
    """
    Search for daily jobs, process them, and create weekly jobs if a is completed.
    """
    try:
        print("Searching for daily jobs")

        if jobs_daily.count_documents({}) == 0:
            print("Nothing to do...")
            return []

        document = jobs_daily.find().sort("date").limit(1).next()
        if document:
            print("###Processing job###")
            print(document)
            bike_date = document.get("date")
            execute_daily_mean(bike_date)
            jobs_daily.delete_one(document)
            print("###Finished job###")
            if document.get("weekday") == 7:
                print("#######Create Weekly Job#######")
                weekly = {"week": 1,
                          "bike_date_first_day": bike_date - timedelta(days=6),
                          "bike_date_last_day": bike_date}
                print(weekly)
                jobs_weekly.insert_one(weekly)
    except:
        print("An exception occurred")
        return []


def job_weekly_bike():
    """
    Search for weekly jobs, process them, and update MongoDB collections.
    """
    try:
        print("Searching for weekly jobs")
        if jobs_weekly.count_documents({}) == 0:
            print("Nothing to do...")
            return []

        document = jobs_weekly.find().limit(1).next()
        if document:
            print("Processing job:")
            print(document)
            bike_date_first_day = document.get("bike_date_first_day")
            bike_date_last_day = document.get("bike_date_last_day")
            execute_weekly_mean(bike_date_first_day, bike_date_last_day)
            jobs_weekly.delete_one(document)
    except:
        print("An exception occurred")
        return []


def execute_daily_mean(date):
    """
    Calculate daily mean ride length and update MongoDB collection.
    """
    spark = SparkSession.builder \
        .appName('daily_average') \
        .master("spark://spark-master:7077") \
        .config("spark.mongodb.read.connection.uri",
                "mongodb://root:example@mongo1:27017/BikeData.BikeRides?authSource=admin") \
        .config("spark.mongodb.write.connection.uri",
                "mongodb://root:example@mongo1:27017/BikeData.Daily?authSource=admin") \
        .config("spark.jars", "/spark/jars/mongo-spark-connector_2.12-10.2.0.jar") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    df = spark.read.format("mongodb").load()

    df_date = df.filter(df['date'] == date).select("*")
    df_mean = df_date.select(_mean(col('ride_length')).alias('mean')).withColumn("rounded_time",
                                                                                 round(col("mean"), 2)).collect()

    mean = df_mean[0]['rounded_time']
    print(mean)

    average_data = [(date, mean)]

    average_columns = ["_id", "average_ride_time"]

    average = spark.createDataFrame(average_data, average_columns)

    average.write.format("mongodb").mode("append").save()
    spark.stop()


def execute_weekly_mean(date_from, date_to):
    """
    Calculate weekly mean ride length and update MongoDB collection.
    """
    spark = SparkSession.builder \
        .appName('my_awesome') \
        .master("spark://spark-master:7077") \
        .config("spark.mongodb.read.connection.uri",
                "mongodb://root:example@mongo1:27017/BikeData.Daily?authSource=admin") \
        .config("spark.mongodb.write.connection.uri",
                "mongodb://root:example@mongo1:27017/BikeData.Weekly?authSource=admin") \
        .config("spark.jars", "/spark/jars/mongo-spark-connector_2.12-10.2.0.jar") \
        .getOrCreate()

    df = spark.read.format("mongodb").load()

    df_date = df.filter(df['_id'] >= date_from).filter(df['_id'] <= date_to)
    df_mean = df_date.select(_mean(col('average_ride_time')).alias('mean')).withColumn("rounded_time",
                                                                                       round(col("mean"), 2)).collect()

    mean = df_mean[0]['rounded_time']
    print(mean)

    average_data = [(date_from, date_to, mean)]

    average_columns = ["start_date", "end_date", "average_ride_time"]

    average = spark.createDataFrame(average_data, average_columns)

    average.write.format("mongodb").mode("append").save()
    spark.stop()


schedule.every(30).seconds.do(job_daily_bike)
schedule.every(30).seconds.do(job_weekly_bike)

print("Scheduler initialized")
while True:
    schedule.run_pending()
    time.sleep(1)
