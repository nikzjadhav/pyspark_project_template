# 🌿 Local Lakehouse with Apache Iceberg, MinIO, Spark, Nessie & Dremio

Data is becoming the cornerstone of modern businesses. As businesses scale, so does their data, and this leads to the need for efficient data storage, retrieval, and processing systems. This is where Data Lakehouses come into the picture.

---

## 🤔 What is a Data Lakehouse?

A Data Lakehouse combines the best of both data lakes and data warehouses. It provides data lakes' raw storage capabilities and data warehouses' structured querying capabilities. This hybrid model ensures flexibility in storing vast amounts of unstructured data, while also enabling SQL-based structured queries, ensuring that businesses can derive meaningful insights from their data.

---

## 🏠 Components of Our Local Lakehouse Setup

We will be implementing a basic lakehouse locally on your laptop with the following components:

- **Apache Spark**: Used for ingesting streaming or batch data into our lakehouse.
- **MinIO**: Acts as our data lake repository with S3-compatible storage.
- **Apache Iceberg**: Table format that enables smart, fast queries on our lakehouse data.
- **Nessie**: Data catalog providing discoverability and Git-like versioning for datasets.
- **Dremio**: Query engine for ad-hoc analytics and BI dashboarding, supports full DML on Iceberg.

> Bonus: Dremio Arctic (cloud managed Nessie) adds UI and automatic optimization features.

---

## 🏢 Create a Docker Compose File and Run It

Building a Data Lakehouse on your local machine requires orchestrating multiple services. Docker Compose helps define and run multi-container Docker applications.

### Steps:

1. **Install Docker**: Download it from [Docker's official site](https://www.docker.com/).

2. **Create Docker Compose File**

Navigate to your project directory and create a file named `docker-compose.yml` with the following content:

```yaml
version: "3.9"

services:
  dremio:
    platform: linux/x86_64
    image: dremio/dremio-oss:latest
    ports:
      - 9047:9047
      - 31010:31010
      - 32010:32010
    container_name: dremio

  minioserver:
    image: minio/minio
    ports:
      - 9000:9000
      - 9001:9001
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    container_name: minio
    command: server /data --console-address ":9001"

  spark_notebook:
    image: alexmerced/spark33-notebook
    ports:
      - 8888:8888
    env_file: .env
    container_name: notebook

  nessie:
    image: projectnessie/nessie
    container_name: nessie
    ports:
      - "19120:19120"

networks:
  default:
    name: iceberg_env
    driver: bridge
```

3. **Create .env File**

In the same directory, create an `.env` file with:

```env
AWS_REGION=us-east-1
MINIO_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxx
AWS_S3_ENDPOINT=http://minioserver:9000
WAREHOUSE=s3a://warehouse/
NESSIE_URI=http://nessie:19120/api/v1
```

4. **Run the Docker Compose Services**

Open **4 terminals**, and run each service individually:

**Terminal 1:**

```bash
docker-compose up minioserver
```

Open [localhost:9001](http://localhost:9001) and log in with `minioadmin`. Then:

- Create bucket: `warehouse`
- Generate access key/secret, and add to `.env`

**Terminal 2:**

```bash
docker-compose up nessie
```

**Terminal 3:**

```bash
docker-compose up spark_notebook
```

Note the tokenized Jupyter link in logs and open in browser.

**Terminal 4:**

```bash
docker-compose up dremio
```

---

## 📒 Create a Table in Spark

In Jupyter, create a notebook and paste this code:

```python
import pyspark
from pyspark.sql import SparkSession
import os

NESSIE_URI = os.environ.get("NESSIE_URI")
WAREHOUSE = os.environ.get("WAREHOUSE")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
AWS_S3_ENDPOINT= os.environ.get("AWS_S3_ENDPOINT")

conf = (
    pyspark.SparkConf()
    .setAppName('app_name')
    .set('spark.jars.packages', 'org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.3.1,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.3_2.12:0.67.0,software.amazon.awssdk:bundle:2.17.178,software.amazon.awssdk:url-connection-client:2.17.178')
    .set('spark.sql.extensions', 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions')
    .set('spark.sql.catalog.nessie', 'org.apache.iceberg.spark.SparkCatalog')
    .set('spark.sql.catalog.nessie.uri', NESSIE_URI)
    .set('spark.sql.catalog.nessie.ref', 'main')
    .set('spark.sql.catalog.nessie.authentication.type', 'NONE')
    .set('spark.sql.catalog.nessie.catalog-impl', 'org.apache.iceberg.nessie.NessieCatalog')
    .set('spark.sql.catalog.nessie.s3.endpoint', AWS_S3_ENDPOINT)
    .set('spark.sql.catalog.nessie.warehouse', WAREHOUSE)
    .set('spark.sql.catalog.nessie.io-impl', 'org.apache.iceberg.aws.s3.S3FileIO')
    .set('spark.hadoop.fs.s3a.access.key', AWS_ACCESS_KEY)
    .set('spark.hadoop.fs.s3a.secret.key', AWS_SECRET_KEY)
)

spark = SparkSession.builder.config(conf=conf).getOrCreate()

spark.sql("CREATE TABLE nessie.names (name STRING) USING iceberg;").show()
spark.sql("INSERT INTO nessie.names VALUES ('Alex Merced'), ('Dipankar Mazumdar'), ('Jason Hughes')").show()
spark.sql("SELECT * FROM nessie.names;").show()
```

Confirm table creation in MinIO.

---

## 📊 Querying the Data in Dremio

1. Open [localhost:9047](http://localhost:9047) and create an admin account.

2. Click **"Add Source"** and choose **"Nessie"**.

3. Configure:

   - **URI**: `http://nessie:19120/api/v2`
   - **Auth**: None (unless enabled)
   - **Storage settings**:
     - Provide access/secret key from MinIO
     - Set:
       ```
       fs.s3a.path.style.access = true
       fs.s3a.endpoint = http://minioserver:9000
       dremio.s3.compat = true
       ```
   - Disable encryption (non-SSL local network)

4. View and query the `names` table directly from the UI!

> Dremio supports full DML on Iceberg, including inserts and table creation.

---

## 🎉 Conclusion

You now have a fully functional, Git-like, SQL-queryable Lakehouse on your laptop:

- Store and manage data with MinIO
- Track metadata changes using Nessie
- Create and query Iceberg tables using Spark or Dremio

This setup is ideal for experimentation, data versioning, and building modern analytics pipelines.

---

## 👉 Learn More

- [LinkedIn Article: Local Lakehouse with Alex Merced](https://www.linkedin.com/pulse/creating-local-data-lakehouse-using-alex-merced/)
- [Project Nessie](https://projectnessie.org/)
- [Apache Iceberg](https://iceberg.apache.org/)
- [MinIO](https://min.io/)
- [Dremio](https://www.dremio.com/)

---

## 💡 Tip

If you'd like to automate this setup or integrate with your project pipeline, consider extending this with GitHub Actions and data validation tools like **Great Expectations**.