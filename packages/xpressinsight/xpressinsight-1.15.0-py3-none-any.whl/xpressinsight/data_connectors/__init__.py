"""
    Xpress Insight Python package
    =============================

    This is an internal development file of the 'xpressinsight' package.
    It defines classes for reading / writing entity values from various
    data-sources.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

from .parquet_connector import ParquetConnector, MoselParquetConnector
from .insight_worker_parquet_connector import (
    ArraysTableDescription,
    ScalarsTableDescription,
    SetTableDescription,
    ConversionDescription,
    InsightWorkerParquetConnector
)
from .rest_api_connector import RestApiConnector
from .table_connector import TableConnector
from .app_data_connector import AppDataConnector
from .data_connector import DataConnector
