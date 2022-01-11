from fastapi import FastAPI
from pyspark.sql.functions import *
from datetime import date
from pyspark.sql import SparkSession

app = FastAPI()
server = app.server()
spark = SparkSession \
    .builder \
    .appName("Python Spark SQL basic example") \
    .getOrCreate()
df = spark.read \
    .format("csv") \
    .option("header", True) \
    .load("./data.csv")

print(df.take(5))
