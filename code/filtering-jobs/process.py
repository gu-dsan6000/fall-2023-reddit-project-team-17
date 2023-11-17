
import os
import logging
import argparse

# Import pyspark and build Spark session
from pyspark.sql.functions import *
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

logging.basicConfig(format='%(asctime)s,%(levelname)s,%(module)s,%(filename)s,%(lineno)d,%(message)s', level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

def main():
    parser = argparse.ArgumentParser(description="app inputs and outputs")
    parser.add_argument("--s3_dataset_path_submissions", type=str, help="Path of dataset in S3 for reddit comments")
    parser.add_argument("--s3_dataset_path_gutenberg", type=str, help="Path of dataset in S3 for reddit submissions")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("PySparkApp").getOrCreate()
    logger.info(f"spark version = {spark.version}")
    
    # This is needed to save RDDs which is the only way to write nested Dataframes into CSV format
    sc = spark.sparkContext
    sc._jsc.hadoopConfiguration().set(
        "mapred.output.committer.class", "org.apache.hadoop.mapred.FileOutputCommitter"
    )

   
    # insert text here to lowercase all the text data and return the data for using in the ipynb

if __name__ == "__main__":
    main()
