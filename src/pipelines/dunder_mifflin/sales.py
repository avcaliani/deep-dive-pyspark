from os import environ as env

from pyspark.sql import DataFrame
from pyspark.sql import functions as f

from pipelines.base import Pipeline
from utils import file, log

TAG = 'Dunder Mifflin Sales'
DATA_PATH = env.get('DATA_PATH', '/data')
BRONZE_PATH = f'{DATA_PATH}/bronze/dunder-mifflin/sales'
OUTPUT_PATH = f'{DATA_PATH}/silver/dunder-mifflin/sales'
CLUSTER_BY = ['branch', 'date']


class SalesPipeline(Pipeline):

    def run(self) -> None:
        log.info(f'{TAG}: STARTED')
        df = file.read_csv(self.spark, BRONZE_PATH)
        log.info(f'{TAG}: PROCESSING')
        file.write_delta(self.spark, self.process(df), OUTPUT_PATH, CLUSTER_BY)
        log.info(f'{TAG}: RESULTS')
        self.show()
        log.info(f'{TAG}: FINISHED')

    def show(self) -> None:
        df = file.read_delta(self.spark, OUTPUT_PATH)
        df.printSchema()
        df.show(5)

    @classmethod
    def process(cls, df: DataFrame) -> DataFrame:
        df = cls.rename_cols(df)
        df = cls.parse_cols(df)
        df = cls.data_quality(df)
        return df

    @classmethod
    def rename_cols(cls, df: DataFrame) -> DataFrame:
        new_names = map(
            lambda c: f.col(c).alias(str(c).strip().replace(' ', '_').lower()),
            df.columns
        )
        return df.select(*list(new_names))

    @classmethod
    def parse_cols(cls, df: DataFrame) -> DataFrame:
        return df \
            .withColumn('date', f.try_to_date(f.col('date'), 'MMMM d, yyyy')) \
            .withColumn('quantity', f.col('quantity').cast('long')) \
            .withColumn('unit_price', f.regexp_replace(f.col('unit_price'), r'\$', '').cast('double')) \
            .withColumn('discount_pct', f.col('discount_pct').cast('double'))

    @classmethod
    def data_quality(cls, df: DataFrame) -> DataFrame:
        return df.filter(
            ~f.col('salesperson').isNull() &
            ~f.col('date').isNull() &
            (f.col('quantity') >= 0)
        )
