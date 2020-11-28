import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config.get('AWS','AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY']=config.get('AWS','AWS_SECRET_ACCESS_KEY')


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
        This function loads song_data from S3, processes songs and artist tables load them back to S3
        
        Parameters:
            spark       = Spark Session
            input_data  = location of song_data where the file is loaded to process
            output_data = location of the results stored
    """
    
    # get filepath to song data file
    song_data = os.path.join(input_data,"song_data/*/*/*/*.json")
    
    
    # read song data file
    songs_df = spark.read.json(song_data)
    
    # create song data view to write SQL queries
    songs_df.createOrReplaceTempView("songs_table")

    # extract columns to create songs table
    songs_table = spark.sql("""
                            SELECT DISTINCT s.song_id, s.title, s.artist_id, s.year, s.duration 
                            FROM songs_table s 
                            WHERE song_id IS NOT NULL """)
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.mode('overwrite').partitionBy("year", "artist_id").parquet(output_data+'songs_table/')

    # extract columns to create artists table
    artists_table = spark.sql(""" SELECT DISTINCT a.artist_id, a.artist_name, a.artist_location, a.artist_latitude, a.artist_longitude 
                                  FROM songs_table a WHERE a.artist_id IS NOT NULL """)
    
    # write artists table to parquet files
    artists_table.mode('overwrite').parquet(output_data+'artists_table/')


def process_log_data(spark, input_data, output_data):
    """
    This function loads log_data from S3, processes songs and artist tables and loaded them back to S3.
    Parameters:
            spark       = Spark Session
            input_data  = location of song_data where the file is loaded to process
            output_data = location of the results stored
    """
    
    # get filepath to log data file
    log_data =os.path.join(input_data,"log_data")

    # read log data file
    log_df = spark.read.json(log_data)
    
    # filter by actions for song plays
    log_df = log_df.filter(log_df.page == 'NextSong')
    
     # created log view to write SQL Queries
    log_df.createOrReplaceTempView("logs_table")

    # extract columns for users table    
    users_table = spark.sql(""" SELECT DISTINCT l.userId as user_id, l.firstName as first_name, l.lastName as last_name, 
                                                  l.gender as gender, l.level as level 
                                  FROM logs_table l WHERE l.userId IS NOT NULL """)
    
    # write users table to parquet files
    users_table.mode('overwrite').parquet(output_data+'users_table/')

    # create timestamp column from original timestamp column
    spark.udf.register("get_timestamp", lambda x : int(datetime.datetime.fromtimestamp(x / 1000.0)))
    
    
    # create datetime column from original timestamp column
    # get_datetime = udf()
    # df = 
    
    # extract columns to create time table
    time_table = spark.sql('''
                                SELECT get_timestamp(l.ts) as start_time,
                                       hour(get_timestamp(l.ts)) as hour,
                                       dayofmonth(get_timestamp(l.ts)) as day,
                                       weekofyear(get_timestamp(l.ts)) as week,
                                       month(get_timestamp(l.ts)) as month,
                                       year(get_timestamp(l.ts)) as year,
                                       dayofweek(get_timestamp(l.ts)) as weekday
                                FROM logs_table l
                                WHERE l.ts IS NOT NULL ''')
    
    # write time table to parquet files partitioned by year and month
    time_table.mode('overwrite').partitionBy("year", "month").parquet(output_data+'time_table/')

     # read in song data to use for songplays table
    song_df = spark.read.parquet(output_data+'songs_table/')


    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = spark.sql('''
                                    SELECT get_timestamp(l.ts) as start_time,
                                           month(get_timestamp(l.ts)) as month,
                                           year(get_timestamp(l.ts)) as year,
                                           l.userId as user_id,
                                           l.level as level,
                                           s.song_id as song_id,
                                           s.artist_id as artist_id,
                                           l.sessionId as session_id,
                                           l.location as location,
                                           l.userAgent as user_agent,
                                    FROM logs_table l 
                                    JOIN songs_table s
                                    ON l.artist = s.artist_name and l.song = s.title''')

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.mode('overwrite').partitionBy("year", "month").parquet(output_data+'songplays_table/')


def main():
    spark = create_spark_session()
    input_data = config.get('IO','INPUT_DATA')
    output_data = config.get('IO','OUTPUT_DATA')
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
