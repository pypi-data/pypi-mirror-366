"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

#
#

#
#
# pylint: disable=invalid-name

#
#
# pylint: disable=unused-import


from packaging import version

polars_version_compatible = False

#
required_polars_version = "0.20.5"

try:
    import polars
    polars_import_succeeded = True

    polars_version = version.parse(polars.__version__)
    if polars_version >= version.parse(required_polars_version):
        polars_version_compatible = True

        from polars import (
            DataFrame, DataType, LazyFrame, Series,
            Boolean, Float32, Float64, Int8, Int16, Int32, Int64, Null, Object, UInt32, Unknown, Utf8,
            col, lit,
            concat,
            from_arrow, read_csv, read_parquet, scan_parquet
        )
        import polars.selectors as selectors

except ModuleNotFoundError:
    polars_import_succeeded = False


#
polars_available = polars_import_succeeded and polars_version_compatible

#
#
if not polars_available:
    #
    #
    class PolarsDataFrameNotAvailable:
        def __init__(self, *args, **kwargs):
            raise TypeError('Polars is not installed in the Python environment.')

    class PolarsSeriesNotAvailable:
        def __init__(self, *args, **kwargs):
            raise TypeError('Polars is not installed in the Python environment.')

    class PolarsLazyFrameNotAvailable:
        def __init__(self, *args, **kwargs):
            raise TypeError('Polars is not installed in the Python environment.')


    DataFrame = PolarsDataFrameNotAvailable
    LazyFrame = PolarsSeriesNotAvailable
    Series = PolarsLazyFrameNotAvailable

    DataType = None
    Boolean = None
    Float32 = None
    Float64 = None
    Int8 = None
    Int16 = None
    Int32 = None
    Int64 = None
    Null = None
    UInt32 = None
    Unknown = None
    Utf8 = None

    col = None
    lit = None

    concat = None
    from_arrow = None
    read_csv = None
    read_parquet = None
    scan_parquet = None

    selectors = None


def check_polars_available() -> None:
    """ Check whether Polars-type entities are available in this environment, raise TypeError if not. """
    if not polars_available:
        if not polars_import_succeeded:
            raise RuntimeError("Polars entities cannot be used as Polars could be loaded from the Python environment.")
        if not polars_version_compatible:
            raise RuntimeError(f"Polars entities cannot be used as installed Polars version is too old"
                               f" (found version {polars.__version__} but {required_polars_version} or later "
                               f"required).")
        #
        raise RuntimeError("Polars entities cannot be used but the reason could not be determined.")
