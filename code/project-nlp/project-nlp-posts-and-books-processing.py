from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import sparknlp
from sparknlp.base import *
from sparknlp.annotator import *
import argparse

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--s3_dataset_path_submissions_bucket", type=str)
parser.add_argument("--s3_dataset_path_gutenberg", type=str)
parser.add_argument("--s3_output_bucket", type=str)
args = parser.parse_args()

def main():
    # Start Spark session with Spark NLP
    spark = SparkSession.builder \
        .appName("Spark NLP with SageMaker") \
        .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:3.3.4") \
        .getOrCreate()

    
    
    
    ##############
    # Submissions
    ##############
    

    required_columns = ['subreddit', 'title', 'selftext', 'score', 'created_utc', 'url']


    # read the full year

    # Read in data from project bucket
    bucket = "project17-bucket-alex"

    # List of 12 directories each containing 1 month of data
    directories = ["project_2022_"+str(i)+"/submissions" for i in range(1,13)]

    # Iterate through 12 directories and merge each monthly data set to create one big data set
    submissions = None
    for directory in directories:
        s3_path = f"s3a://{args.s3_dataset_path_submissions_bucket}/{directory}"
        month_df = spark.read.parquet(s3_path).select(*required_columns)

        if submissions is None:
            submissions = month_df
        else:
            submissions = submissions.union(month_df)

    submissions = submissions_active
            
    # The regular expression pattern
    pattern = r"(?i)^(.*?)(?=Edit:|$)"

    # Apply the regular expression to create a new column with the modified text
    submissions_active = submissions_active.withColumn("selftext_modified", regexp_extract(col("selftext"), pattern, 1))
    
    
    # story
    story_length = 4500

    submissions_active = submissions_active.filter(length(col("selftext")) > story_length)
    
    # Calculate the approximate percentile of the 'score' column
    quantile_value = submissions_active.approxQuantile("score", [0.85], 0.05)  # 0.05 is the relative error

    # Filter the DataFrame to keep scores above or equal to this value
    submissions_active = submissions_active.filter(col("score") >= quantile_value[0])
    
    # keep only text col
    submissions_active = submissions_active.select("selftext")
    submissions_df = submissions_df.withColumnRenamed("selftext", "text")


    
    
    #############
    #books
    ##########
        
        
    # gutenberg books    
    gutenberg_books = spark.read.text(args.s3_dataset_path_gutenberg)
    gutenberg_books = gutenberg_books.withColumnRenamed("value", "text")

    
    #########
    #clean
    #########
    
    
    from pyspark.sql.functions import udf
    from pyspark.sql.types import ArrayType, IntegerType
    import string

    # Start Spark NLP pipeline
    document_assembler = DocumentAssembler() \
        .setInputCol("text") \
        .setOutputCol("document")

    tokenizer = Tokenizer() \
        .setInputCols(["document"]) \
        .setOutputCol("token")

    normalizer = Normalizer() \
        .setInputCols(["token"]) \
        .setOutputCol("normalized") \
        .setLowercase(True) \
        .setPattern("[^A-Za-z0-9 .,!?;]") \
        .setReplacement(" ")

    finisher = Finisher() \
        .setInputCols(["normalized"]) \
        .setOutputCols(["clean_text"]) \
        .setOutputAsArray(True) \
        .setCleanAnnotations(True)

    # Define the pipeline
    from pyspark.ml import Pipeline

    pipeline = Pipeline().setStages([
        document_assembler,
        tokenizer,
        normalizer,
        finisher
    ])

    # Apply the pipeline to the submissions and books DataFrames
    submissions_active_df = pipeline.fit(submissions_active).transform(submissions_active)
    gutenberg_books_df = pipeline.fit(gutenberg_books).transform(gutenberg_books)
    
    
    def chars_to_ints(text):
        vocab = sorted(set("".join(text)))  # Create a vocabulary from the cleaned text
        char2idx = {c: i for i, c in enumerate(vocab)}
        return [char2idx.get(c, 0) for c in "".join(text)]  # Convert each char in text to its integer representation

    chars_to_ints_udf = udf(chars_to_ints, ArrayType(IntegerType()))

    # Apply the UDF to the 'clean_text' column
    submissions_active_df = submissions_active_df.withColumn("text_as_int", chars_to_ints_udf(col("clean_text")))
    gutenberg_books_df = gutenberg_books_df.withColumn("text_as_int", chars_to_ints_udf(col("clean_text")))


    # output paths
    submissions_output_path = f"s3://{args.s3_output_bucket}/submissions"
    gutenberg_output_path = f"s3://{args.s3_output_bucket}/gutenberg"

    # save output
    submissions_active_df.write.mode("overwrite").parquet(submissions_output_path)
    gutenberg_books_df.write.mode("overwrite").parquet(gutenberg_output_path)

    
    
    

if __name__ == "__main__":
    main()
