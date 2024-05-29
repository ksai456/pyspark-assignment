from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from sqlalchemy import create_engine, text
import pandas as pd
from pyspark.sql.functions import col, count, avg, countDistinct, to_date, first, last, lead, lag, lit, element_at, split, max
from pyspark.sql.types import StringType, StructField, IntegerType, StructType, TimestampType

# Create a SparkSession
def create_spark_session():
    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
        .getOrCreate()
    return spark

def close_spark_session(spark):
    spark.stop()

# PostgreSQL connection properties
postgres_url = "jdbc:postgresql://host.docker.internal:5432/database"
postgres_properties = {
    "user": "username",
    "password": "password",
    "driver": "org.postgresql.Driver"
}

# Hive connection properties
hive_properties = {
    "hive.metastore.uris": "host.docker.internal",
    "hive.server2.thrift.port": "10000",
}

# Read data from PostgreSQL table
def read_postgres_table(spark, table_name):
    return spark.read \
        .jdbc(url=postgres_url, table=table_name, properties=postgres_properties)

# Read data from Hive table
def read_hive_table(curr, table_name):
    return curr.execute(text(f"SELECT * FROM {table_name} LIMIT 5"))


#main method
def main():
    spark = create_spark_session()
    # Read data from PostgreSQL table
    postgres_df = read_postgres_table(spark, "click_session")
    user_df = postgres_df.withColumn("event_date", to_date(col("timestamp")))
    spec =  Window.partitionBy("country", "event_date", "user_id").orderBy("timestamp")
    user_df = user_df.withColumn("last_click", lead(col("timestamp")).over(spec))
    user_df = user_df.withColumn("time_spent", (col("last_click").cast("long") - col("timestamp").cast("long"))/60)
    agg_df = user_df.groupBy("url", "country", "event_date").agg(
        avg("time_spent").alias("average_minutes_spent"),
        countDistinct("user_id").alias("unique_users_count"),
        count("click_event_id").alias("click_count")
        )
    df = agg_df.toPandas()
    # Create a SQLAlchemy engine
    port = 10000
    engine = create_engine(f'hive://host.docker.internal:{port}/')
    # Create a connection to the engine
    conn = engine.connect()
    # Create a cursor object using the connection
    curr = conn.cursor()
    # Create a Hive table
    curr.execute(text("CREATE TABLE IF NOT EXISTS url_metrics (url STRING, country STRING, event_date DATE, average_minutes_spent FLOAT, unique_users_count INT, click_count INT)"))

    # Write data to Hive table
    df.to_sql("url_metrics", con=engine, if_exists="replace", index=False, method="multi")

    # Read data from Hive table
    df_hive = read_hive_table(curr, "url_metrics")
    print(df_hive.fetchall())
    close_spark_session(spark)
    curr.close()


# Perform operations on the dataframes
# ...

# Close the SparkSession
# spark.stop()