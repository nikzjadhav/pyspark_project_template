from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("CSV to Iceberg via REST Catalog") \
    .config("spark.sql.catalog.my_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.my_catalog.catalog-impl", "org.apache.iceberg.rest.RESTCatalog") \
    .config("spark.sql.catalog.my_catalog.uri", "http://rest-catalog:8181") \
    .config("spark.sql.catalog.my_catalog.warehouse", "s3a://warehouse/") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minio") \
    .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

df = spark.read.option("header", "true").csv("/opt/spark-apps/users.csv")
df.writeTo("my_catalog.default.users").createOrReplace()

print("✅ Data written to Iceberg via REST catalog")

spark.stop()
