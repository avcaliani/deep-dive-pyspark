from pipeline.base import Pipeline
from pipeline.dunder_mifflin.sales import SalesPipeline

PIPELINES: dict[str, type[Pipeline]] = {
    'dunder-mifflin-sales': SalesPipeline,
}

__all__ = ['Pipeline', 'SalesPipeline', 'PIPELINES']
