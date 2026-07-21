import argparse

from pyspark.sql import SparkSession

from pipeline import PIPELINES
from utils import log


def spark_session() -> SparkSession:
    return SparkSession \
        .builder \
        .appName('the-paper-trail') \
        .getOrCreate()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run a PySpark pipeline.')
    parser.add_argument(
        '-p', '--pipeline',
        required=True,
        choices=sorted(PIPELINES),
        help='Name of the pipeline to run.',
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    spark = spark_session()
    log.info(f'Spark Version: {spark.version}')
    try:
        PIPELINES[args.pipeline](spark).run()
    except Exception as ex:
        log.error(f"Unexpected Error! {ex}")
    finally:
        spark.stop()
