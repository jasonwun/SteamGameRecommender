import org.apache.spark.ml.feature._
import org.apache.spark.ml.linalg._
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._

// read file
val path = "FinalProject/Game_vector/*"
val df = spark.read.parquet(path)
val isNoneZeroVector = udf({v: Vector => v.numNonzeros > 0}, DataTypes.BooleanType)
val new_df = df.filter(isNoneZeroVector(col("feature_developers")))
               .filter(isNoneZeroVector(col("feature_publishers")))
               .filter(isNoneZeroVector(col("feature_description")))
               .filter(isNoneZeroVector(col("feature_about_the_game")))
               .filter(isNoneZeroVector(col("feature_device_requirements")))
               .filter(isNoneZeroVector(col("feature_geners")))
               .filter(isNoneZeroVector(col("feature_categories")))

//calculate feature_developers distance 
//calculate feature_publishers distance
//calculate feature_description
//calculate feature_about_the_game
//calculate feature_device_requirements
//calculate feature_geners
//calculate feature_categories
val mh_developer = new MinHashLSH().setNumHashTables(3).setInputCol("feature_developers").setOutputCol("developers_Values")
val mh_publishers = new MinHashLSH().setNumHashTables(3).setInputCol("feature_publishers").setOutputCol("publishers_hashValues")
val mh_description = new MinHashLSH().setNumHashTables(3).setInputCol("feature_description").setOutputCol("description_Values")
val mh_about_the_game = new MinHashLSH().setNumHashTables(3).setInputCol("feature_about_the_game").setOutputCol("about_the_game_Values")
val mh_device_requirements = new MinHashLSH().setNumHashTables(3).setInputCol("feature_device_requirements").setOutputCol("device_Values")
val mh_geners = new MinHashLSH().setNumHashTables(3).setInputCol("feature_geners").setOutputCol("geners_Values")
val mh_categories = new MinHashLSH().setNumHashTables(3).setInputCol("feature_categories").setOutputCol("categories_Values")

val model_developer = mh_developer.fit(new_df)
val model_publishers = mh_publishers.fit(new_df)
val model_description = mh_description.fit(new_df)
val model_about_the_game = mh_about_the_game.fit(new_df)
val model_device_requirements = mh_device_requirements.fit(new_df)
val model_geners = mh_geners.fit(new_df)
val model_categories = mh_categories.fit(new_df)

import org.apache.spark.sql.Row
val developer_key = new_df.where("steam_appid == 271590").select("feature_developers").rdd.map { case Row(v: Vector) => v}.first
val publishers_key = new_df.where("steam_appid == 271590").select("feature_publishers").rdd.map { case Row(v: Vector) => v}.first
val description_key = new_df.where("steam_appid == 271590").select("feature_description").rdd.map { case Row(v: Vector) => v}.first
val about_the_game_key = new_df.where("steam_appid == 271590").select("feature_about_the_game").rdd.map { case Row(v: Vector) => v}.first
val categories_key = new_df.where("steam_appid == 271590").select("feature_categories").rdd.map { case Row(v: Vector) => v}.first
val geners_key = new_df.where("steam_appid == 271590").select("feature_geners").rdd.map { case Row(v: Vector) => v}.first
val device_key = new_df.where("steam_appid == 271590").select("feature_device_requirements").rdd.map { case Row(v: Vector) => v}.first

val geners_df = model_geners.approxNearestNeighbors(new_df, geners_key, 500).filter("steam_appid != 271590").filter("distCol == 0")

val description_df = model_description.approxNearestNeighbors(geners_df, description_key, 500)
val about_the_game_df = model_about_the_game.approxNearestNeighbors(geners_df, about_the_game_key, 500)

val add_weight = (p: Double) => udf( (x: Double) => x + p ) 
val device_df = model_device_requirements.approxNearestNeighbors(geners_df, device_key, 500).withColumn("distCol", add_weight(0.1)($"distCol"))

val id_list = new_df.select("steam_appid").collect()

new_df.createOrReplaceTempView("game_list")
for (id <- id_list) {
    print(id)
    val string_id = id.toString.dropRight(1).substring(1)
    val s_description = "select feature_description from game_list where steam_appid = "
    val s_about_the_game = "select feature_about_the_game from game_list where steam_appid = "
    val s_geners = "select feature_geners from game_list where steam_appid = "
    val s_device = "select feature_device_requirements from game_list where steam_appid = "
    
    val final_description = s_description.concat(string_id)
    val final_about_the_game = s_about_the_game.concat(string_id)
    val final_geners = s_geners.concat(string_id)
    val final_device = s_device.concat(string_id)

    val description_key =sqlContext.sql(final_description).rdd.map { case Row(v: Vector) => v}.first
    val about_the_game_key = sqlContext.sql(final_about_the_game).rdd.map { case Row(v: Vector) => v}.first   
    val geners_key = sqlContext.sql(final_geners).rdd.map { case Row(v: Vector) => v}.first
    val device_key = sqlContext.sql(final_device).rdd.map { case Row(v: Vector) => v}.first

    val temp_geners_df = model_geners.approxNearestNeighbors(new_df, geners_key, 500)
    temp_geners_df.createOrReplaceTempView("geners_df")
    val s_filter = "select * from geners_df where distCol = 0 and steam_appid != "
    val final_filter = s_filter.concat(id.toString.dropRight(1).substring(1))
    
    val geners_df = sqlContext.sql(final_filter)
    val description_df = model_description.approxNearestNeighbors(geners_df, description_key, 500)
    val about_the_game_df = model_about_the_game.approxNearestNeighbors(geners_df, about_the_game_key, 500)
    val add_weight = (p: Double) => udf( (x: Double) => x + p ) 
    val device_df = model_device_requirements.approxNearestNeighbors(geners_df, device_key, 500).withColumn("distCol", add_weight(0.1)($"distCol"))
    
    val new_description_df = description_df.select("steam_appid", "name", "header_image", "distCol")
    val new_about_the_game_df = about_the_game_df.select("steam_appid", "name", "header_image", "distCol")
    val new_device_df = device_df.select("steam_appid", "header_image", "name", "distCol")

    val temp = new_description_df.union(new_about_the_game_df)
    val temp2 = temp.union(new_device_df)
    val recommand_df = temp2.dropDuplicates("steam_appid").orderBy(asc("distCol"))
    val recommand_20 = recommand_df.limit(20)
    //recommand_20.show()
    val file_name = "FinalProject/Recommandation/" + string_id
    recommand_20.write.mode("overwrite").parquet(file_name)
}
System.exit(0)
