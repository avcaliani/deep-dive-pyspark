from datetime import date

import pytest
from pyspark.sql.types import DateType, DoubleType, LongType, StringType, StructField, StructType
from pyspark.testing.utils import assertDataFrameEqual

from pipelines.dunder_mifflin.sales import SalesPipeline

COLUMNS = ['sale_id', 'date', 'branch', 'salesperson', 'client', 'product', 'quantity', 'unit_price', 'discount_pct']

# Schema for rows already in parse_cols' output shape.
# Typed, so a lone None in a single-row DataFrame doesn't defeat Spark's 
# type inference
PARSED_SCHEMA = StructType([
    StructField('sale_id', StringType()),
    StructField('date', DateType()),
    StructField('branch', StringType()),
    StructField('salesperson', StringType()),
    StructField('client', StringType()),
    StructField('product', StringType()),
    StructField('quantity', LongType()),
    StructField('unit_price', DoubleType()),
    StructField('discount_pct', DoubleType()),
])


def test_rename_cols(spark):
    df = spark.createDataFrame(
        [('1', 'January 5, 2024', 'Scranton', 'Jim Halpert', 'Acme', 'Copy Paper', '10', '$12.50', '5')],
        ['Sale Id', ' DATE ', 'Branch', 'Salesperson', 'Client', 'Product', 'Quantity', 'Unit Price', 'Discount Pct'],
    )
    result = SalesPipeline.rename_cols(df)
    assert result.columns == COLUMNS

@pytest.mark.parametrize('row, expected_row', [
    pytest.param(
        ('1', 'January 5, 2024', 'Scranton', 'Jim Halpert', 'Acme', 'Copy Paper', '10', '$12.50', '5'),
        ('1', date(2024, 1, 5), 'Scranton', 'Jim Halpert', 'Acme', 'Copy Paper', 10, 12.50, 5.0),
        id='clean row',
    ),
    pytest.param(
        ('2', '', 'Scranton', 'Michael Scott', 'Acme', 'Toner', '-3', '$99.99', '0'),
        ('2', None, 'Scranton', 'Michael Scott', 'Acme', 'Toner', -3, 99.99, 0.0),
        id='missing date parses to null instead of raising under ANSI mode',
    ),
])
def test_parse_cols(spark, row, expected_row):
    df = spark.createDataFrame([row], COLUMNS)
    assertDataFrameEqual(
        actual = SalesPipeline.parse_cols(df), 
        expected = spark.createDataFrame(
            [expected_row], 
            PARSED_SCHEMA
        )
    )


CLEAN_ROW = ('1', date(2024, 1, 5), 'Scranton', 'Jim Halpert', 'Acme', 'Copy Paper', 10, 12.50, 5.0)


@pytest.mark.parametrize('row, kept', [
    pytest.param(CLEAN_ROW, True, id='clean row'),
    pytest.param(
        ('2', None, 'Scranton', 'Michael Scott', 'Acme', 'Toner', 5, 99.99, 0.0),
        False, 
        id='missing date',
    ),
    pytest.param(
        ('3', date(2024, 1, 6), 'Scranton', None, 'Acme', 'Labels', 2, 5.00, 0.0),
        False, 
        id='missing salesperson',
    ),
    pytest.param(
        ('4', date(2024, 1, 7), 'Scranton', 'Dwight Schrute', 'Acme', 'Envelopes', -3, 3.00, 0.0),
        False, 
        id="negative quantity (Michael's prank returns)",
    ),
])
def test_data_quality(spark, row, kept):
    df = spark.createDataFrame([row], PARSED_SCHEMA)
    assertDataFrameEqual(
        SalesPipeline.data_quality(df), 
        df if kept else spark.createDataFrame([], PARSED_SCHEMA)
    )
