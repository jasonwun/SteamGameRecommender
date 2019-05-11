import findspark
findspark.init('/share/apps/spark/spark-2.1.0-bin-hadoop2.6')
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.ml.feature import Tokenizer, RegexTokenizer
from pyspark.sql.functions import col, udf, regexp_replace
from pyspark.sql.types import IntegerType
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import CountVectorizer

ssc = SparkSession.builder.config("spark.executor.memory", "70g").config("spark.driver.memory", "50g").config("spark.memory.offHeap.enabled",True).config("spark.memory.offHeap.size","16g").appName('clean data').getOrCreate()

directKafkaStream = KafkaUtils.createDirectStream(ssc, ["my-topic"], {"metadata.broker.list": ['compute-1-1.local:9092']})
