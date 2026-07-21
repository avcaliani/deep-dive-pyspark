from pipeline.base import Pipeline
from pipeline.dunder_mifflin_sales import DunderMifflinSalesPipeline

PIPELINES: dict[str, type[Pipeline]] = {
    'dunder-mifflin-sales': DunderMifflinSalesPipeline,
}

__all__ = ['Pipeline', 'DunderMifflinSalesPipeline', 'PIPELINES']
