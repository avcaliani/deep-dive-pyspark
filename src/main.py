from pyspark.sql import SparkSession

from pipeline import DunderMifflinSalesPipeline
from utils import log

# TODO: Setup ArgParse to receive the pipeline name -p | --pipeline
# In the main, parse the arguments and trigger the pipeline according to the pipeline name

# Also, create an trait/abstract class Pipeline that forces the run() method implementation


def spark_session() -> SparkSession:
    return SparkSession \
        .builder \
        .appName('pyspark-app') \
        .getOrCreate()


if __name__ == '__main__':
    spark = spark_session()
    log.info(f'Spark Version: {spark.version}')
    try:
        DunderMifflinSalesPipeline(spark).run()
    except Exception as ex:
        log.error(f"Unexpected Error! {ex}")
    finally:
        spark.stop()
