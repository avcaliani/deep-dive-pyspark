#!/bin/bash -xe
# @author       Anthony Vilarim Caliani
# @contact      github.com/avcaliani

cd "$(dirname "$0")/.."

uv sync --frozen

if [ ! -d "data/bronze/dunder-mifflin-sales" ]; then
  scripts/generate_sales_data.sh
fi

uv run spark-submit --master local \
  --files resources/log4j.properties \
  --packages "io.delta:delta-spark_2.13:4.2.0" \
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" \
  --driver-java-options "-Dlog4j2.configurationFile=file:resources/log4j.properties" \
  'src/main.py' "$@"
