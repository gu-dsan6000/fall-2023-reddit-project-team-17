
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
    #parser.add_argument("--s3_dataset_path_commments", type=str, help="Path of dataset in S3 for reddit comments")
    parser.add_argument("--s3_dataset_path_submissions", type=str, help="Path of dataset in S3 for reddit submissions")
    parser.add_argument("--s3_dataset_path_books", type=str, help="Path of dataset in S3 for gubenberg books")
    parser.add_argument("--s3_output_bucket", type=str, help="s3 output bucket")
    parser.add_argument("--s3_output_prefix", type=str, help="s3 output prefix")
    #parser.add_argument("--subreddits", type=str, help="comma separate list of subreddits of interest")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("PySparkApp").getOrCreate()
    logger.info(f"spark version = {spark.version}")
    
    # This is needed to save RDDs which is the only way to write nested Dataframes into CSV format
    sc = spark.sparkContext
    sc._jsc.hadoopConfiguration().set(
        "mapred.output.committer.class", "org.apache.hadoop.mapred.FileOutputCommitter"
    )

    ###### Submissions ###
    
    
    required_columns = ['subreddit', 'title', 'selftext', 'score', 'created_utc', 'url']

    # read the full year

    # Read in data from project bucket
    #bucket = "project17-bucket-alex"

    # List of 12 directories each containing 1 month of data
    directories = ["project_2022_"+str(i)+"/submissions" for i in range(1,13)]

    # Iterate through 12 directories and merge each monthly data set to create one big data set
    submissions = None
    for directory in directories:
        s3_path = f"s3a://{args.s3_output_bucket}/{directory}"
        month_df = spark.read.parquet(s3_path).select(*required_columns)

        if submissions is None:
            submissions = month_df
        else:
            submissions = submissions.union(month_df)

    
    #submissions = spark.read.parquet(args.s3_dataset_path_submissions, header=True)
    #submissions = spark.read.text(args.s3_dataset_path_submissions)
    s3_path = f"s3://{args.s3_output_bucket}/{args.s3_output_prefix}/submissions"
    logger.info(f"going to write submissions for submissions in {s3_path}")
    submissions.write.mode("overwrite").parquet(s3_path)
    
    
    
    
    
    
    books = spark.read.text(args.s3_dataset_path_books)
    s3_path = f"s3://{args.s3_output_bucket}/{args.s3_output_prefix}/books"
    logger.info(f"going to write submissions for books in {s3_path}")
    books.write.mode("overwrite").parquet(s3_path)

    
if __name__ == "__main__":
    main()
