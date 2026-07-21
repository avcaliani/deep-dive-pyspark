import inspect
from logging import Logger

from pyspark.context import SparkContext


def __caller_name() -> str:
    events = inspect.stack()
    if len(events) < 3:
        return __name__
    return inspect.getmodule(events[3][0]).__name__


def __logger() -> Logger:
    sc = SparkContext.getOrCreate()
    log4j = sc._jvm.org.apache.logging.log4j
    return log4j.LogManager.getLogger(__caller_name())


def info(msg: str) -> None:
    __logger().info(msg)


def error(msg: str) -> None:
    __logger().error(msg)
