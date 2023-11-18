
import os
import logging
import argparse


import json
import sparknlp
import numpy as np
import pandas as pd
from sparknlp.base import *
from pyspark.ml import Pipeline
from sparknlp.annotator import *
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from sparknlp.pretrained import PretrainedPipeline


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


#!pip install spark-nlp
#from sparknlp.annotator import *
#from sparknlp.base import *
#import sparknlp


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
            
            

    submissions_small = submissions.sample(withReplacement=False, fraction=0.001, seed=42)


    # create small dfs
    use_small = True  # to easily swap between the small and small dfs
    submissions_active = submissions_small if use_small else submissions


    def clean_submissions(df: DataFrame) -> DataFrame:

        # define conditions
        conditions = (col('selftext') != "[removed]") & (col('selftext') != "[deleted]") & (col('selftext').isNotNull() & (col('selftext') != ""))


        # apply filter
        cleaned_df = df.filter(conditions)


        return cleaned_df

    submissions_active = clean_submissions(submissions_active)


    # use regex the remove text after 'Edit: ' or 'edit: '

    # The regular expression pattern
    pattern = r"(?i)^(.*?)(?=Edit:|$)"

    # Apply the regular expression to create a new column with the modified text
    submissions_active = submissions_active.withColumn("selftext_modified", regexp_extract(col("selftext"), pattern, 1))


    # define stories as posts longer than a certain length 
    story_length = 4500

    submissions_active = submissions_active.filter(length(col("selftext")) > story_length)


    # keep only the 25% most engaging posts
    # Calculate the approximate percentile of the 'score' column
    quantile_value = submissions_active.approxQuantile("score", [0.85], 0.05)  # 0.05 is the relative error

    # Filter the DataFrame to keep scores above or equal to this value
    submissions_active = submissions_active.filter(col("score") >= quantile_value[0])
    
    
    # take only selftext
    submissions_active = submissions_active.select("selftext")
    
    submissions_active = submissions_active.withColumnRenamed("selftext", "text")


    ########
    # books
    #######
    
    
    books = spark.read.text(args.s3_dataset_path_books)
    

    
    
    # change col name
    books = books.withColumnRenamed("value", "text")

    
    #s3_path = f"s3://{args.s3_output_bucket}/{args.s3_output_prefix}/books"
    #logger.info(f"going to write submissions for books in {s3_path}")
    #books.write.mode("overwrite").parquet(s3_path)
    

    #s3_path = f"s3://{args.s3_output_bucket}/{args.s3_output_prefix}/submissions"
    #logger.info(f"going to write submissions for submissions in {s3_path}")
    #submissions_active.write.mode("overwrite").parquet(s3_path)
    
    
    all_model_text = books.unionByName(submissions_active)
        
        
        
        
    s3_path = f"s3://{args.s3_output_bucket}/{args.s3_output_prefix}/all-model-text"
    logger.info(f"going to write submissions for submissions in {s3_path}")
    all_model_text.write.mode("overwrite").parquet(s3_path)
    
    
    

    
if __name__ == "__main__":
    main()
