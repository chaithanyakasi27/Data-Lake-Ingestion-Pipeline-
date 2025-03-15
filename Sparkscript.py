import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, month, year
import json

# Initialize boto3 client to access AWS Secrets Manager
secrets_manager_client = boto3.client('secretsmanager', region_name="us-east-1")

# Fetch AWS credentials from Secrets Manager
aws_secret = secrets_manager_client.get_secret_value(SecretId="AWSKEYS")
aws_credentials = json.loads(aws_secret['SecretString'])

# Debugging: Print available keys in Secrets Manager response
print("AWS Credentials Retrieved:", aws_credentials.keys())

# Correct key names (Check if they match what you stored in AWS Secrets Manager)
AWS_ACCESS_KEY = aws_credentials.get('AWS_ACCESS_KEY')  # Commonly used key name
AWS_SECRET_KEY = aws_credentials.get('AWS_SECRET_KEY')  # Commonly used key name
AWS_REGION = aws_credentials.get('AWS_REGION', 'us-east-1')  # Default to us-east-1 if missing

if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise ValueError("AWS access key or secret key not found in Secrets Manager!")

# Fetch PostgreSQL credentials from Secrets Manager
postgres_secret = secrets_manager_client.get_secret_value(SecretId="POSTGRESQL")
postgres_credentials = json.loads(postgres_secret['SecretString'])

POSTGRES_HOST = postgres_credentials.get('POSTGRES_HOST')
POSTGRES_USER = postgres_credentials.get('POSTGRES_USER')
POSTGRES_PASSWORD = postgres_credentials.get('POSTGRES_PASSWORD')
POSTGRES_DB = postgres_credentials.get('POSTGRES_DB')
POSTGRES_PORT = postgres_credentials.get('POSTGRES_PORT')

if not all([POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT]):
    raise ValueError("Missing PostgreSQL credentials in Secrets Manager!")

# Initialize Spark Session with S3 and PostgreSQL configurations
spark = SparkSession.builder.appName("PostgresToS3Transfer").getOrCreate()

# Configure AWS S3 access
hadoop_conf = spark._jsc.hadoopConfiguration()
hadoop_conf.set("fs.s3a.access.key", AWS_ACCESS_KEY)
hadoop_conf.set("fs.s3a.secret.key", AWS_SECRET_KEY)
hadoop_conf.set("fs.s3a.endpoint", f"s3.{AWS_REGION}.amazonaws.com")
hadoop_conf.set("fs.s3a.path.style.access", "true")

# PostgreSQL JDBC URL
jdbc_url = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Read data from PostgreSQL table
df = spark.read.format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "public.mockrecord") \
    .option("user", POSTGRES_USER) \
    .option("password", POSTGRES_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .load()

# Extract month and year from the start_date_time column
df_with_month_year = df.withColumn("month", month(col("start_date_time"))) \
                       .withColumn("year", year(col("start_date_time")))

# Clean the data (if needed)
df_cleaned = df_with_month_year.withColumn("questions_list", concat_ws(",", col("questions_list")))

# Display data (optional)
df_cleaned.show()

# Write the data to S3 in CSV format, partitioned by year and month
df_cleaned.write.option("header", True) \
    .partitionBy("year", "month") \
    .mode("overwrite") \
    .csv("s3://uexpertlyrecords/raw_layers/year-2025/month-feb/day-05-records/")

# Stop Spark Session
spark.stop()
