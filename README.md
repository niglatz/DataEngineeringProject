# Data Engineering Project
# Batch-Processing-Based Data Architecture for a Data-Intensive Application

This data engineering project is a robust data architecture designed for a data-intensive application, specifically tailored to simulate a machine learning data pipeline using the [Divvy Cyclistics](https://www.kaggle.com/datasets/je1429387/divvy-analysis-520421?select=all_trips_v2.csv) dataset. This dataset consists of 3.5 million unique bike share rides taken by users between May 2020 and April 2021.
## Objective
The primary goal of this project is to ingest, store, and process the data through batch processing in order to compute daily and weekly averages of bike rides. The resulting statistics will serve as the basis for a machine learning application, although the application itself is beyond the scope of this project.

![Pipeline Overview](pipeline.png)

## Data Ingestion
Data ingestion is orchestrated by an Apache Kafka cluster with two brokers, chosen for replication and reliability. This design not only increases reliability. It also contributes to the scalability of the system. The coordination of these brokers is managed by Zookeeper. The process starts with a producer reading raw data from the CSV file containing the bicycle trip information. 
This producer then writes the data to the "bike rides" topic within the data stream. On the consumer side, a consumer reads this data from the stream and writes the raw information to the database.

## Data Storage
For data storage, MongoDB is used with a replica set consisting of one primary node and two secondary nodes. This configuration  increases the reliability of the entire pipeline.
## Batch Processing
Batch processing is performed by an Apache Spark cluster with one master and two worker nodes. This setup is chosen for both reliability and scalability.
## Getting Started
To start the pipeline, simply run the following command:

```bash
docker-compose up -d
```

# Mongo Express Access
Mongo Express facilitates easy access to MongoDB. You can reach it at [http://localhost:8081/](http://localhost:8081/) with the following credentials:

- **Username:** admin
- **Password:** pass
