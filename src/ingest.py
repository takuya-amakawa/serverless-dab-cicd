# Databricks notebook source
# ingest.py — サンプル（サーバーレスで実行）。catalog/schema はジョブパラメータで受ける。
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

print(f"[ingest] target = {catalog}.{schema}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
spark.sql(f"CREATE TABLE IF NOT EXISTS {catalog}.{schema}.sample_ingest (id INT, ts TIMESTAMP) USING DELTA")
spark.sql(f"INSERT INTO {catalog}.{schema}.sample_ingest VALUES (1, current_timestamp())")
print("[ingest] done")
