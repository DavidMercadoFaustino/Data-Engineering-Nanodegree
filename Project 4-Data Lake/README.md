# **S3 DataLake**

The aim of this project is to create an ETL pipeline using the data stored in S3 buckets and process that data into respective Fact and dimension tables using spark and then upload the parquet files back to S3.

## **Prerequisites**

* Install Python 3.x.
* Also install conda and pyspark
* Connection to EMR cluster

## **Datasets** 
* Song Data: s3a://udacity-denanodegree/song_data 
* Log Data: s3a://udacity-dend/log-data

## **Schema**

A Star Schema is used.

### **Fact Table**

* **songplays_table:** records in event data associated with song plays i.e. records with page NextSong songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

### **Dimension Tables**

* **users_table:** users in the app user_id, first_name, last_name, gender, level

* **songs_table:** songs in music database song_id, title, artist_id, year, duration

* **artists_table:** artists in music database artist_id, name, location, lattitude, longitude

* **time_table:** timestamps of records in songplays broken down into specific units start_time, hour, day, week, month, year, weekday

## **Pipeline**

* Load the Data which are in JSON Files(Song Data and Log Data) 
* Use Spark to process these JSON files and then generate a set of Fact and Dimension Tables 
* Load back this data to S3

## **Execution Steps:** 
* Insert your AWS IAM credential in dl.cfg
* Create EMR cluster
* Copy elt.py and dl.cfg to EMR terminal
* Run etl.py in EMR terminal