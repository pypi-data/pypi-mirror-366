from __future__ import annotations

from typing import Type, Any

import dask
import dask.dataframe as dd
import pandas as pd
from sqlalchemy import (
    inspect,
    select
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base
import time
from sqlalchemy.exc import TimeoutError as SASQLTimeoutError, OperationalError
import sqlalchemy as sa

from sibi_dst.utils import ManagedResource
from sibi_dst.df_helper.core import FilterHandler


class SQLAlchemyDask(ManagedResource):
    """
    Loads data from a database into a Dask DataFrame using a memory-safe,
    non-parallel, paginated approach.

    This class avoids using a numeric `index_col for parallel loading.
    """

    _SQLALCHEMY_TO_DASK_DTYPE = {
        "INTEGER": "Int64",
        "SMALLINT": "Int64",
        "BIGINT": "Int64",
        "FLOAT": "float64",
        "NUMERIC": "float64",
        "BOOLEAN": "bool",
        "VARCHAR": "object",
        "TEXT": "object",
        "DATE": "datetime64[ns]",
        "DATETIME": "datetime64[ns]",
        "TIME": "object",
        "UUID": "object",
    }

    def __init__(
            self,
            model: Type[declarative_base()],
            filters: dict,
            engine: Engine,
            chunk_size: int = 1000,
            **kwargs
    ):
        """
        Initializes the data loader.

        Args:
            model: The SQLAlchemy ORM model for the table.
            filters: A dictionary of filters to apply to the query.
            engine: An SQLAlchemy Engine instance.
            chunk_size: The number of records to fetch in each database query.
            logger: A logger instance.
            debug: Whether to enable detailed logging.
        """
        super().__init__(**kwargs)
        self.model = model
        self.filters = filters
        self.engine = engine
        self.chunk_size = chunk_size
        self.filter_handler_cls = FilterHandler
        self.total_records = -1 # Initialize to -1 to indicate uncounted

    @classmethod
    def infer_meta_from_model(cls, model: Type[declarative_base()]) -> dict:
        """
        Infers a metadata dictionary for Dask based on the SQLAlchemy model.
        This helps Dask understand the DataFrame structure without reading data.
        """
        mapper = inspect(model)
        dtypes = {}
        for column in mapper.columns:
            dtype_str = str(column.type).upper().split("(")[0]
            dtype = cls._SQLALCHEMY_TO_DASK_DTYPE.get(dtype_str, "object")
            dtypes[column.name] = dtype
        return dtypes

    def read_frame(self, fillna_value=None) -> tuple[int | Any, Any] | Any:
        """
        Builds and executes a query to load data into a Dask DataFrame.

        This method works by first running a COUNT query to get the total
        size, then creating a series of delayed tasks that each fetch a
        chunk of data using LIMIT/OFFSET.

        Args:
            fillna_value: Value to replace NaN or NULL values with, if any.

        Returns:
            A lazy Dask DataFrame.
        """
        # 1. Build the base query and apply filters
        query = select(self.model)
        if self.filters:
            query = self.filter_handler_cls(
                backend="sqlalchemy", logger=self.logger, debug=self.debug
            ).apply_filters(query, model=self.model, filters=self.filters)
        else:
            query = query.limit(self.chunk_size)
        if self.verbose:
            self.logger.debug(f"Base query for pagination: {query}")

        # 2. Get metadata for the Dask DataFrame structure
        ordered_columns = [column.name for column in self.model.__table__.columns]
        meta_dtypes = self.infer_meta_from_model(self.model)
        meta_df = pd.DataFrame(columns=ordered_columns).astype(meta_dtypes)

        # 3. Get the total record count to calculate the number of chunks

        retry_attempts = 3
        backoff_factor = 0.5  # start with a 0.5-second delay
        total_records = 0

        for attempt in range(retry_attempts):
            try:
                with self.engine.connect() as connection:
                    count_query = sa.select(sa.func.count()).select_from(query.alias())
                    total_records = connection.execute(count_query).scalar_one()

                # If successful, break the loop
                break

            except SASQLTimeoutError:
                if attempt < retry_attempts - 1:
                    self.logger.warning(
                        f"Connection pool limit reached. Retrying in {backoff_factor} seconds..."
                    )
                    time.sleep(backoff_factor)
                    backoff_factor *= 2  # Double the backoff time for the next attempt
                else:
                    self.total_records = -1  # Indicate failure to count records
                    self.logger.error(
                        "Failed to get a connection from the pool after several retries.",
                        exc_info=True
                    )
                    return self.total_records, dd.from_pandas(meta_df, npartitions=1)
            except OperationalError as oe:
                # sometimes the DB driver wraps timeouts in OperationalError
                if "timeout" in str(oe).lower():
                    self.logger.warning("OperationalTimeout, retrying…", exc_info=True)
                    time.sleep(backoff_factor)
                    backoff_factor *= 2
                    continue
                else:
                    self.total_records = -1  # Indicate failure to count records
                    self.logger.error("OperationalError", exc_info=True)
                    return self.total_records, dd.from_pandas(meta_df, npartitions=1)
            except Exception as e:
                self.total_records = -1  # Indicate failure to count records
                self.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
                return self.total_records, dd.from_pandas(meta_df, npartitions=1)

        self.total_records = total_records
        if total_records == 0:
            self.logger.warning("Query returned 0 records.")
            return self.total_records, dd.from_pandas(meta_df, npartitions=1)

        self.logger.debug(f"Total records to fetch: {total_records}. Chunk size: {self.chunk_size}.")

        # 4. Create a list of Dask Delayed objects, one for each chunk
        @dask.delayed
        def get_chunk(sql_query, chunk_offset):
            """A Dask-delayed function to fetch one chunk of data."""
            # LIMIT/OFFSET must be applied in the delayed function
            paginated_query = sql_query.limit(self.chunk_size).offset(chunk_offset)
            df = pd.read_sql(paginated_query, self.engine)

            if fillna_value is not None:
                df = df.fillna(fillna_value)

            # Ensure column order and types match the meta
            return df[ordered_columns].astype(meta_dtypes)

        offsets = range(0, total_records, self.chunk_size)
        delayed_chunks = [get_chunk(query, offset) for offset in offsets]

        # 5. Construct the final lazy Dask DataFrame from the delayed chunks
        ddf = dd.from_delayed(delayed_chunks, meta=meta_df)
        self.logger.debug(f"Successfully created a lazy Dask DataFrame with {ddf.npartitions} partitions.")
        if not self._entered:
            super().cleanup()
        return self.total_records, ddf

## Dask-Only Solution to test in better hardware

# from typing import Type, Dict, Any
# import math
# import time
# import pandas as pd
# import dask
# import dask.dataframe as dd
#
# import sqlalchemy as sa
# from sqlalchemy import select, func
# from sqlalchemy.engine import Engine
# from sqlalchemy.exc import TimeoutError as SASQLTimeoutError, OperationalError
# from sqlalchemy.orm import declarative_base
#
# from sibi_dst.df_helper.core import FilterHandler
# from sibi_dst.utils import Logger
#
#
# class SQLAlchemyDask:
#     """
#     Loads data into a Dask DataFrame.  If there’s exactly one integer PK,
#     use dask.dataframe.read_sql_table; otherwise fall back to offset‐based
#     pagination pushed into dask.delayed to keep memory use minimal.
#     """
#
#     def __init__(
#         self,
#         model: Type[declarative_base()],
#         filters: Dict[str, Any],
#         engine: Engine,
#         chunk_size: int = 1_000,
#         logger=None,
#         debug: bool = False,
#     ):
#         self.model      = model
#         self.filters    = filters or {}
#         self.engine     = engine
#         self.chunk_size = chunk_size
#         self.logger     = logger or Logger.default_logger(self.__class__.__name__)
#         self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)
#         self.filter_handler_cls = FilterHandler
#         self.debug = debug
#
#     def read_frame(self, fillna_value=None) -> dd.DataFrame:
#         # 1) Build base query + filters
#         base_q = select(self.model)
#         if self.filters:
#             base_q = self.filter_handler_cls(
#                 backend="sqlalchemy",
#                 logger=self.logger,
#                 debug=self.debug,
#             ).apply_filters(base_q, model=self.model, filters=self.filters)
#
#         # 2) Zero-row meta for dtype inference
#         meta = pd.read_sql_query(base_q.limit(0), self.engine).iloc[:0]
#         if meta.shape[1] == 0:
#             self.logger.warning("No columns detected; returning empty DataFrame.")
#             return dd.from_pandas(meta, npartitions=1)
#
#         # 3) Single‐PK parallel path?
#         pk_cols = list(self.model.__table__.primary_key.columns)
#         if (
#             len(pk_cols) == 1
#             and pd.api.types.is_integer_dtype(meta[pk_cols[0].name])
#         ):
#             try:
#                 return self._ddf_via_read_sql_table(pk_cols[0], meta, fillna_value)
#             except Exception:
#                 self.logger.warning(
#                     "read_sql_table path failed, falling back to offset pagination",
#                     exc_info=True,
#                 )
#
#         # 4) Composite PK or fallback → offset pagination in delayed tasks
#         return self._offset_paginated_ddf(base_q, meta, fillna_value)
#
#     def _offset_paginated_ddf(self, base_q, meta, fillna):
#         # 1) count total rows
#         try:
#             with self.engine.connect() as conn:
#                 total = conn.execute(
#                     select(func.count()).select_from(base_q.alias())
#                 ).scalar_one()
#         except Exception:
#             self.logger.error("Failed to count records; returning empty DataFrame", exc_info=True)
#             return dd.from_pandas(meta, npartitions=1)
#
#         if total == 0:
#             self.logger.warning("Query returned 0 records.")
#             return dd.from_pandas(meta, npartitions=1)
#         self.logger.debug(f"Total records to fetch: {total}. Chunk size: {self.chunk_size}.")
#         # 2) create delayed tasks per offset
#         @dask.delayed
#         def _fetch_chunk(offset: int) -> pd.DataFrame:
#             q = base_q.limit(self.chunk_size).offset(offset)
#             df = pd.read_sql_query(q, self.engine)
#             if fillna is not None:
#                 df = df.fillna(fillna)
#             return df[meta.columns].astype(meta.dtypes.to_dict())
#
#         offsets = range(0, total, self.chunk_size)
#         parts = [_fetch_chunk(off) for off in offsets]
#
#         ddf = dd.from_delayed(parts, meta=meta)
#         self.logger.debug(f"Offset‐paginated read → {len(parts)} partitions")
#         return ddf
#
#     def _ddf_via_read_sql_table(self, pk_col, meta, fillna) -> dd.DataFrame:
#         # same as before: min/max + dd.read_sql_table
#         backoff = 0.5
#         for attempt in range(3):
#             try:
#                 with self.engine.connect() as conn:
#                     min_id, max_id = conn.execute(
#                         select(func.min(pk_col), func.max(pk_col))
#                         .select_from(self.model.__table__)
#                     ).one()
#                 break
#             except (SASQLTimeoutError, OperationalError) as e:
#                 if "timeout" in str(e).lower() and attempt < 2:
#                     self.logger.warning(f"Timeout fetching PK bounds; retrying in {backoff}s")
#                     time.sleep(backoff)
#                     backoff *= 2
#                 else:
#                     raise
#
#         if min_id is None or max_id is None:
#             self.logger.warning("Table empty—no PK bounds.")
#             return dd.from_pandas(meta, npartitions=1)
#
#         total = max_id - min_id + 1
#         nparts = max(1, math.ceil(total / self.chunk_size))
#         ddf = dd.read_sql_table(
#             table=self.model.__table__.name,
#             uri=str(self.engine.url),
#             index_col=pk_col.name,
#             limits=(min_id, max_id),
#             npartitions=nparts,
#             columns=list(meta.columns),
#         )
#         if fillna is not None:
#             ddf = ddf.fillna(fillna)
#         self.logger.debug(f"Parallel read via dask.read_sql_table → {nparts} partitions")
#         return ddf
