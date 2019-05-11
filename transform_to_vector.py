from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.ml.feature import Tokenizer, RegexTokenizer
from pyspark.sql.functions import col, udf, regexp_replace
from pyspark.sql.types import IntegerType
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import CountVectorizer


if __name__ == "__main__":
	print("start")
	spark = SparkSession.builder.appName('clean data').getOrCreate()

	Path = "FinalProject/game_list.json"
	df = spark.read.json(Path)
	
	df.createOrReplaceTempView("game")
	data = df.groupBy("type").agg(f.countDistinct("steam_appid"))

	df.createOrReplaceTempView("game")
	data = spark.sql("SELECT steam_appid, platforms, detailed_description, genres.description as geners, required_age, "
	                   "about_the_game, developers, publishers, pc_requirements, supported_languages, "
	                   "categories.description as categories, name, linux_requirements, mac_requirements, "
	                   " header_image FROM game where type == 'game'")
	data = data.withColumn("device_requirements", f.concat(f.col("pc_requirements"), 
	                                                       f.lit(" "), f.col("linux_requirements"),
	                                                        f.lit(" "), f.col("mac_requirements")))
	data.createOrReplaceTempView("filtered")

	selected_data = spark.sql("SELECT steam_appid, name, detailed_description,"
	                          "about_the_game, geners, categories, developers, publishers, "
	                          "device_requirements, header_image from filtered ")
	# remove null
	selected_data = selected_data.where(f.col("geners").isNotNull())
	selected_data = selected_data.where(f.col("categories").isNotNull())
	selected_data = selected_data.where(f.col("developers").isNotNull())
	selected_data = selected_data.where(f.col("detailed_description").isNotNull())
	selected_data = selected_data.where(f.col("about_the_game").isNotNull())
	selected_data = selected_data.where(f.col("publishers").isNotNull())
	selected_data = selected_data.where(f.col("device_requirements").isNotNull())

	#clean detailed description

	#remove html char
	selected_data = selected_data.withColumn("detailed_description", f.regexp_replace("detailed_description", '\<.*?\>', ""))

	#remove special char
	selected_data = selected_data.withColumn("detailed_description", f.regexp_replace("detailed_description", '[^a-zA-Z ]', ""))

	#tokenize the description
	tokenizer = Tokenizer(inputCol="detailed_description", outputCol="token_description")
	selected_data = tokenizer.transform(selected_data)

	# remove stop words in the token
	remover = StopWordsRemover(inputCol="token_description", outputCol="filtered_description")
	selected_data = remover.transform(selected_data)

	# vectorize the description
	vocabSize = 100000
	cv = CountVectorizer(inputCol="filtered_description", outputCol="feature_description", vocabSize=vocabSize, minDF=100)
	cv_model = cv.fit(selected_data)
	selected_data = cv_model.transform(selected_data)

	#clean about the game

	#remove html char
	selected_data = selected_data.withColumn("about_the_game", f.regexp_replace("about_the_game", '\<.*?\>', ""))

	#remove special char
	selected_data = selected_data.withColumn("about_the_game", f.regexp_replace("about_the_game", '[^a-zA-Z ]', ""))


	#tokenize the about the game
	tokenizer = Tokenizer(inputCol="about_the_game", outputCol="token_about_the_game")
	selected_data = tokenizer.transform(selected_data)

	# remove stop words in the token
	remover = StopWordsRemover(inputCol="token_about_the_game", outputCol="filtered_about_the_game")
	selected_data = remover.transform(selected_data)

	# vectorize the about the game
	vocabSize = 1000000
	cv = CountVectorizer(inputCol="filtered_about_the_game", outputCol="feature_about_the_game", vocabSize=vocabSize, minDF=1)
	cv_model = cv.fit(selected_data)
	selected_data = cv_model.transform(selected_data)

	#remove html char
	selected_data = selected_data.withColumn("device_requirements", f.regexp_replace("device_requirements", '\<.*?\>', ""))

	#remove special char
	selected_data = selected_data.withColumn("device_requirements", f.regexp_replace("device_requirements", '[^a-zA-Z0-9 ]', ""))

	#tokenize the device requirements
	tokenizer = Tokenizer(inputCol="device_requirements", outputCol="token_device_requirements")
	selected_data = tokenizer.transform(selected_data)

	# remove stop words in the token
	remover = StopWordsRemover(inputCol="token_device_requirements", outputCol="filtered_device_requirements")
	selected_data = remover.transform(selected_data)

	# vectorize the device requirements
	vocabSize = 50000
	cv = CountVectorizer(inputCol="filtered_device_requirements", outputCol="feature_device_requirements", vocabSize=vocabSize, minDF=2)
	cv_model = cv.fit(selected_data)
	selected_data = cv_model.transform(selected_data)

	# clean geners
	vocabSize = 500
	cv = CountVectorizer(inputCol="geners", outputCol="feature_geners", vocabSize=vocabSize, minDF=10)
	cv_model = cv.fit(selected_data)
	selected_data = cv_model.transform(selected_data)

	# clean categories
	vocabSize = 500
	cv = CountVectorizer(inputCol="categories", outputCol="feature_categories", vocabSize=vocabSize, minDF=10)
	cv_model = cv.fit(selected_data)
	selected_data = cv_model.transform(selected_data)

	# clean developer
	vocabSize = 100000
	cv = CountVectorizer(inputCol="developers", outputCol="feature_developers", vocabSize=vocabSize, minDF=1)
	cv_model = cv.fit(selected_data)
	selected_data = cv_model.transform(selected_data)

	# clean publishers
	vocabSize = 100000
	cv = CountVectorizer(inputCol="publishers", outputCol="feature_publishers", vocabSize=vocabSize, minDF=1)
	cv_model = cv.fit(selected_data)
	selected_data = cv_model.transform(selected_data)

	cleaned_data = selected_data.select("steam_appid", "name", 
                                    "feature_developers", "feature_publishers", "feature_description", 
                                    "feature_about_the_game", 
                                    "feature_device_requirements", "feature_geners", "feature_categories")
	cleaned_data.write.mode('overwrite').parquet("FinalProject/Game_vector")
	print("end")

	