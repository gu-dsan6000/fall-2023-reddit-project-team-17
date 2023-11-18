
import os
import sys
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

logging.basicConfig(format='%(asctime)s,%(levelname)s,%(module)s,%(filename)s,%(lineno)d,%(message)s', level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

def main():
    parser = argparse.ArgumentParser(description="app inputs and outputs")
    parser.add_argument("--s3_dataset_path", type=str, help="Path of dataset in S3")
    parser.add_argument("--s3_output_bucket", type=str, help="s3 output bucket")
    parser.add_argument("--s3_output_key_prefix", type=str, help="s3 output key prefix")
    args = parser.parse_args()
    logger.info(f"args={args}")
    
    spark = SparkSession.builder \
    .appName("Spark NLP")\
    .config("spark.driver.memory","16G")\
    .config("spark.driver.maxResultSize", "0") \
    .config("spark.kryoserializer.buffer.max", "2000M")\
    .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:5.1.3")\
    .getOrCreate()
    
    logger.info(f"Spark version: {spark.version}")
    logger.info(f"sparknlp version: {sparknlp.version()}")
    
    # This is needed to save RDDs which is the only way to write nested Dataframes into CSV format
    sc = spark.sparkContext
    sc._jsc.hadoopConfiguration().set(
        "mapred.output.committer.class", "org.apache.hadoop.mapred.FileOutputCommitter"
    )

    # Defining the schema corresponding to the input data. The input data does not contain the headers
    schema = StructType(
        [
            StructField("ID", StringType(), True),
            StructField("Content", StringType(), True),
            StructField("Summary", StringType(), True),
            StructField("Dataset", StringType(), True)
        ]
    )
    
    # Downloading the data from S3 into a Dataframe
    logger.info(f"going to read {args.s3_dataset_path}")
    #df = spark.read.parquet(args.s3_dataset_path, header=True, schema=schema)
    #df = df.repartition(64)
    
        # Read in data from project bucket
    #bucket = "project17-bucket-alex"
    #output_prefix_data = "project_2022"

    # List of 12 directories each containing 1 month of data
    directories = ["project_2022_"+str(i)+"/submissions" for i in range(1,13)]

    # Iterate through 12 directories and merge each monthly data set to create one big data set
    df = None
    for directory in directories:
        s3_path = f"s3a://{bucket}/{directory}"
        month_df = spark.read.parquet(s3_path, header = True)

        if df is None:
            df = month_df
        else:
            df = df.union(month_df)
    logger.info(f"finished reading files...")
    
    submissions = df

    # Here we subset the submissions to only include posts from r/AmItheAsshole for the subsequent analysis
    raw_aita = submissions.filter(F.col('subreddit') == "AmItheAsshole")

    # filter submissions to remove deleted/removed posts
    aita = raw_aita.filter((F.col('selftext') != '[removed]') & (F.col('selftext') != '[deleted]' ))

    # Filter submissions to only include posts tagged with the 4 primary flairs
    acceptable_flairs = ['Everyone Sucks', 'Not the A-hole', 'No A-holes here', 'Asshole']
    df_flairs = aita.where(F.col('link_flair_text').isin(acceptable_flairs))
    #df_flairs.select("subreddit", "author", "title", "selftext", "created_utc", "num_comments", "link_flair_text").show()
    #print(f"shape of the subsetted submissions dataframe of appropriately flaired posts is {df_flairs.count():,}x{len(df_flairs.columns)}")
    df = df_flairs

    
    # get count
    row_count = df.count()
    # create a temp rdd and save to s3
    line = [f"count={row_count}"]
    logger.info(line)
    l = [('count', row_count)]
    tmp_df = spark.createDataFrame(l)
    s3_path = "s3://" + os.path.join(args.s3_output_bucket, args.s3_output_key_prefix, "count")
    logger.info(f"going to save count to {s3_path}")
    # we want to write to a single file so coalesce
    tmp_df.coalesce(1).write.format('csv').option('header', 'false').mode("overwrite").save(s3_path)
    
    #df = df\
    #.withColumn('politics', F.col("Content").rlike("""(?i)politics|(?i)political|(?i)senate|(?i)democrats|(?i)republicans|(?i)government|(?i)president|(?i)prime minister|(?i)congress"""))\
    #.withColumn('sports', F.col("Content").rlike("""(?i)sport|(?i)ball|(?i)coach|(?i)goal|(?i)baseball|(?i)football|(?i)basketball"""))\
    #.withColumn('arts', F.col("Content").rlike("""(?i)art|(?i)painting|(?i)artist|(?i)museum|(?i)photography|(?i)sculpture"""))\
    #.withColumn('history', F.col("Content").rlike("""(?i)history|(?i)historical|(?i)ancient|(?i)archaeology|(?i)heritage|(?i)fossil""")).persist()
    
    #categories = ['politics', 'arts', 'sports', 'history']
    #for c in categories:
    #    df_soln = df.groupBy(c).count() #.toPandas().to_dict(orient='records')        
    #    s3_path = "s3://" + os.path.join(args.s3_output_bucket, args.s3_output_key_prefix, c)
    #    logger.info(f"going to save dataframe to {s3_path}")
    #    # we want to write to a single file so coalesce
    #    df_soln.coalesce(1).write.format('csv').option('header', 'false').mode("overwrite").save(s3_path)

    # sentiment analysis
    MODEL_NAME = 'sentimentdl_use_twitter'
    logger.info(f"setting up an nlp pipeline with model={MODEL_NAME}")
    documentAssembler = DocumentAssembler()\
    .setInputCol("selftext")\
    .setOutputCol("document")
    
    use = UniversalSentenceEncoder.pretrained(name="tfhub_use", lang="en")\
     .setInputCols(["document"])\
     .setOutputCol("sentence_embeddings")

    sentimentdl = SentimentDLModel.pretrained(name=MODEL_NAME, lang="en")\
    .setInputCols(["sentence_embeddings"])\
    .setOutputCol("sentiment")

    nlp_pipeline = Pipeline(
      stages = [
          documentAssembler,
          use,
          sentimentdl
      ])
    logger.info(f"going to fit and transform pipeline on dataframe")
    pipeline_model = nlp_pipeline.fit(df)
    results = pipeline_model.transform(df)
    logger.info(f"done with fit and transform pipeline on dataframe")
    
    results=results.withColumn('sentiment', F.explode(results.sentiment.result))
    final_data=results.select("subreddit", "author", "title", "selftext", "created_utc", "num_comments", "link_flair_text",'sentiment')
    final_data.persist()
    #final_data.show()
    cols = ['link_flair_text', 'sentiment']
    #logger.info(f"going to run a group by and count on columns={cols}")
    sum_counts = final_data.groupBy(cols).count()
    logger.info(f"going to convert sum_counts to dict")
    df_sent_baseline = sum_counts #.toPandas().to_dict(orient='records')
    logger.info(df_sent_baseline)
    s3_path = "s3://" + os.path.join(args.s3_output_bucket, args.s3_output_key_prefix, "sentiment_baseline")
    logger.info(f"going to save dataframe to {s3_path}")
    # we want to write to a single file so coalesce
    df_sent_baseline.coalesce(1).write.format('csv').option('header', 'false').mode("overwrite").save(s3_path)
    logger.info("all done")
    
if __name__ == "__main__":
    main()
