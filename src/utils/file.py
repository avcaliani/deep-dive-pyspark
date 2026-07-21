import os

from delta.tables import DeltaTable
from pyspark.sql import DataFrame
from pyspark.sql.session import SparkSession


def read_csv(spark: SparkSession, path: str) -> DataFrame:
    return spark \
        .read \
        .option('delimiter', ',') \
        .option('header', 'true') \
        .csv(path)


def write_delta(spark: SparkSession, df: DataFrame, path: str, cluster_by: list[str]) -> None:
    # DeltaTable.createOrReplace(...).location(path) builds SQL internally
    # (delta.`{path}`), and a relative path starting with ./ breaks that
    # parser (INVALID_ATTRIBUTE_NAME_SYNTAX) -- normalize to absolute first.
    path = os.path.abspath(path)
    if DeltaTable.isDeltaTable(spark, path):
        # Table already exists with its CLUSTER BY spec set, clear rows via 
        # DELETE rather than mode('overwrite'), since overwrite rewrites
        # the table definition itself and silently drops the clustering metadata
        DeltaTable.forPath(spark, path).delete()
    else:
        DeltaTable.createOrReplace(spark) \
            .addColumns(df.schema) \
            .clusterBy(*cluster_by) \
            .location(path) \
            .execute()
    df.write \
        .format('delta') \
        .mode('append') \
        .save(path)


def read_delta(spark: SparkSession, path: str) -> DataFrame:
    return spark \
        .read \
        .format('delta') \
        .load(path)
