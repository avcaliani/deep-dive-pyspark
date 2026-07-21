from abc import ABC, abstractmethod

from pyspark.sql import SparkSession


class Pipeline(ABC):

    def __init__(self, spark: SparkSession):
        self.spark = spark

    @abstractmethod
    def run(self) -> None:
        ...
