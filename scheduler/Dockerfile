# Verwende das Basisimage
FROM bde2020/spark-python-template:3.3.0-hadoop3.3

RUN pip3 install pymongo
RUN pip3 install schedule

# Kopiere das JAR-File in den gemeinsamen Workspace
COPY mongodb-driver-core-4.8.2.jar /spark/jars/
COPY bson-4.8.2.jar /spark/jars/
COPY bson-record-codec-4.8.2.jar /spark/jars/
COPY mongodb-driver-sync-4.8.2.jar /spark/jars/
COPY mongo-spark-connector_2.12-10.2.0.jar /spark/jars/

COPY scheduler.py /app/

ENV SPARK_APPLICATION_PYTHON_LOCATION /app/scheduler.py