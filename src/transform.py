# transform.py — サンプル（spark_python_task, サーバーレス）。引数: catalog schema
import sys
from pyspark.sql import SparkSession

catalog = sys.argv[1] if len(sys.argv) > 1 else ""
schema = sys.argv[2] if len(sys.argv) > 2 else ""

spark = SparkSession.builder.getOrCreate()
print(f"[transform] source = {catalog}.{schema}.sample_ingest")
df = spark.table(f"{catalog}.{schema}.sample_ingest")
df.groupBy().count().show()
print("[transform] done")
