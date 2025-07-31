from __future__ import annotations

import warnings
from typing import Any, Dict, Optional, Union, TypeVar

import dask.dataframe as dd
import pandas as pd
from pydantic import BaseModel

from sibi_dst.df_helper.core import QueryConfig, ParamsConfig, FilterHandler
from sibi_dst.utils import ManagedResource
from sibi_dst.utils import ParquetSaver, ClickHouseWriter
from .backends.http import HttpConfig
from .backends.parquet import ParquetConfig
from .backends.sqlalchemy import SqlAlchemyConnectionConfig, SqlAlchemyLoadFromDb

warnings.filterwarnings("ignore")
T = TypeVar("T", bound=BaseModel)


# --- Backend Strategy Pattern Implementation ---

class BaseBackend:
    """Abstract base class defining clear sync and async loading interfaces."""

    def __init__(self, helper: DfHelper):
        self.helper = helper
        self.logger = helper.logger
        self.debug = helper.debug
        self.total_records = helper.total_records  # no records loaded yet
        self._entered = helper._entered  # Track if the helper is used in a context manager

    def load(self, **options) -> tuple[Any, Any] | Union[dd.DataFrame | pd.DataFrame]:
        """Synchronous data loading method. Must be implemented by sync backends."""
        raise NotImplementedError(f"Backend '{self.__class__.__name__}' does not support synchronous loading.")

    async def aload(self, **options) -> tuple[Any, Any] | Union[dd.DataFrame | pd.DataFrame]:
        """Asynchronous data loading method. By default, it calls the sync version."""
        return self.load(**options)


class SqlAlchemyBackend(BaseBackend):
    def load(self, **options) -> tuple[Any, Any] | Union[dd.DataFrame | pd.DataFrame]:
        try:
            # Process incoming filter options into the ParamsConfig object
            if options and hasattr(self.helper._backend_params, 'parse_params'):
                self.helper._backend_params.parse_params(options)

            db_loader = SqlAlchemyLoadFromDb(
                plugin_sqlalchemy=self.helper.backend_db_connection,
                plugin_query=self.helper._backend_query,
                plugin_params=self.helper._backend_params,
                logger=self.logger,
                debug=self.debug
            )
            self.total_records, result = db_loader.build_and_load()
            return self.total_records, result
        except Exception as e:
            self.logger.error(f"Failed to load data from sqlalchemy: {e}", exc_info=self.debug)
            return -1, dd.from_pandas(pd.DataFrame(), npartitions=1)


class ParquetBackend(BaseBackend):
    """This backend is also purely synchronous."""

    def load(self, **options) -> tuple[Any, Any] | Union[dd.DataFrame | pd.DataFrame]:
        try:
            df = self.helper.backend_parquet.load_files()
            if options and df is not None:
                df = FilterHandler('dask', logger=self.logger, debug=False).apply_filters(df, filters=options)

            df = df.persist()

            self.total_records = len(df) or -1  # If df is empty, set total_records to -1
            return self.total_records, df
        except Exception as e:
            self.total_records = -1  # Reset total_records on failure
            self.logger.error(f"Failed to load data from parquet: {e}", exc_info=True)
            return -1, dd.from_pandas(pd.DataFrame(), npartitions=1)


class HttpBackend(BaseBackend):
    """This backend is purely asynchronous."""

    def load(self, **options) -> tuple[Any, Any] | Union[dd.DataFrame | pd.DataFrame]:
        # This will correctly fail by raising NotImplementedError from the base class.
        return self.helper.backend_http.fetch_data(**options)

    async def aload(self, **options) -> tuple[Any, Any] | Union[pd.DataFrame, dd.DataFrame]:
        if not self.helper.backend_http:
            self.logger.warning("HTTP plugin not configured properly.")
            self.total_records = -1
            return self.total_records, dd.from_pandas(pd.DataFrame(), npartitions=1)
        result = await self.helper.backend_http.fetch_data(**options)
        self.total_records = len(result)
        return self.total_records, result


# --- Main DfHelper Facade Class ---

class DfHelper(ManagedResource):
    """
    A reusable utility for loading data. It provides both sync (`load`) and
    async (`aload`) methods to accommodate different backends.
    """
    _BACKEND_STRATEGIES = {
        'sqlalchemy': SqlAlchemyBackend,
        'parquet': ParquetBackend,
        'http': HttpBackend,
    }

    _BACKEND_ATTR_MAP = {
        'sqlalchemy': 'backend_db_connection',
        'parquet': 'backend_parquet',
        'http': 'backend_http',
    }

    default_config: Dict = None

    def __init__(self, backend='sqlalchemy', **kwargs):
        self.default_config = self.default_config or {}
        kwargs = {**self.default_config.copy(), **kwargs}
        super().__init__(**kwargs)
        self.backend = backend

        # Need to set default values for backend-specific configurations
        kwargs.setdefault("debug", self.debug)
        kwargs.setdefault("fs", self.fs)
        kwargs.setdefault("logger", self.logger)
        self.total_records = -1  # Initialize total_records to -1 to indicate no records loaded yet
        self._backend_query = self._get_config(QueryConfig, kwargs)
        self._backend_params = self._get_config(ParamsConfig, kwargs)
        self.backend_db_connection: Optional[SqlAlchemyConnectionConfig] = None
        self.backend_parquet: Optional[ParquetConfig] = None
        self.backend_http: Optional[HttpConfig] = None

        if self.backend == 'sqlalchemy':
            self.backend_db_connection = self._get_config(SqlAlchemyConnectionConfig, kwargs)
        elif self.backend == 'parquet':
            self.backend_parquet = self._get_config(ParquetConfig, kwargs)
        elif self.backend == 'http':
            self.backend_http = self._get_config(HttpConfig, kwargs)

        strategy_class = self._BACKEND_STRATEGIES.get(self.backend)
        if not strategy_class: raise ValueError(f"Unsupported backend: {self.backend}")
        self.backend_strategy = strategy_class(self)

    def __exit__(self, exc_type, exc_value, traceback):
        self._cleanup()
        super().__exit__(exc_type, exc_value, traceback)

    def _cleanup(self):
        attr_name = self._BACKEND_ATTR_MAP.get(self.backend)
        if not attr_name:
            self.logger.warning(f"No attribute mapping found for backend '{self.backend}'. Cleanup skipped.")
            return
        # Get the actual config object (e.g., self.backend_db_connection)
        active_config = getattr(self, attr_name, None)

        if active_config and hasattr(active_config, "close"):
            self.logger.debug(f"Closing resources for '{self.backend}' backend using attribute '{attr_name}'.")
            active_config.close()

    def _get_config(self, model: T, kwargs: Dict[str, Any]) -> T:
        recognized_keys = set(model.model_fields.keys())
        model_kwargs = {k: kwargs[k] for k in recognized_keys if k in kwargs}
        return model(**model_kwargs)

    def load(self, as_pandas=False, **options) -> Union[pd.DataFrame, dd.DataFrame]:
        """Loads data synchronously. Fails if backend is async-only."""
        self.logger.debug(f"Loading data from {self.backend} backend with options: {options}")
        self.total_records, df = self.backend_strategy.load(**options)
        df = self._process_loaded_data(df)
        df = self._post_process_df(df)
        if not self._entered:
            self.logger.warning(
                "DfHelper instance was not used in a context manager; cleanup is being called manually.")
            self._cleanup()
        return df.compute() if as_pandas else df

    async def aload(self, as_pandas=False, **options) -> Union[pd.DataFrame, dd.DataFrame]:
        """Loads data asynchronously from any backend."""
        self.total_records, df = await self.backend_strategy.aload(**options)
        df = self._process_loaded_data(df)
        df = self._post_process_df(df)
        return df.compute() if as_pandas else df

    def _post_process_df(self, df: dd.DataFrame) -> dd.DataFrame:
        df_params = self._backend_params.df_params
        if not df_params: return df
        fieldnames, column_names, index_col = (df_params.get("fieldnames"), df_params.get("column_names"),
                                               df_params.get("index_col"))
        if not any([fieldnames, column_names, index_col]): return df
        self.logger.debug("Post-processing DataFrame.")
        if fieldnames:
            valid_fieldnames = [f for f in fieldnames if f in df.columns]
            if len(valid_fieldnames) < len(fieldnames): self.logger.warning(
                f"Missing columns for filtering: {set(fieldnames) - set(valid_fieldnames)}")
            df = df[valid_fieldnames]
        if column_names:
            if len(df.columns) != len(column_names): raise ValueError(
                f"Length mismatch: DataFrame has {len(df.columns)} columns, but {len(column_names)} names were provided.")
            df = df.rename(columns=dict(zip(df.columns, column_names)))
        if index_col:
            if index_col not in df.columns: raise ValueError(f"Index column '{index_col}' not found in DataFrame.")
            df = df.set_index(index_col)
        return df

    def _process_loaded_data(self, df: dd.DataFrame) -> dd.DataFrame:
        field_map = self._backend_params.field_map or {}
        if not isinstance(field_map, dict) or not field_map: return df
        if hasattr(df, 'npartitions') and df.npartitions == 1 and not len(df.head(1)): return df
        self.logger.debug("Processing loaded data...")
        rename_mapping = {k: v for k, v in field_map.items() if k in df.columns}
        if rename_mapping: df = df.rename(columns=rename_mapping)
        return df

    def save_to_parquet(self, df: dd.DataFrame, parquet_filename: str, **kwargs):
        if hasattr(df, 'npartitions') and df.npartitions == 1 and not len(df.head(1)):
            self.logger.warning("Cannot save to parquet; DataFrame is empty.")
            return
        fs = kwargs.pop('fs', self.fs)
        if not fs:
            raise ValueError("Filesystem (fs) must be provided to save to parquet.")
        path = kwargs.pop('parquet_storage_path', None)
        if not path:
            raise ValueError("parquet_storage_path must be provided to save to parquet.")
        writer_config = {
            'df_result': df,
            'parquet_storage_path': path,
            'fs': fs,
            'debug': self.debug,
            'logger': self.logger,
            'verbose': self.verbose,
        }
        with ParquetSaver(**writer_config) as saver:
            saver.save_to_parquet(parquet_filename)

        self.logger.debug(f"Parquet saved to {parquet_filename} in {path}.")

    def save_to_clickhouse(self, df: dd.DataFrame, **credentials):
        if hasattr(df, 'npartitions') and df.npartitions == 1 and not len(df.head(1)):
            self.logger.warning("Cannot write to ClickHouse; DataFrame is empty.")
            return

        with ClickHouseWriter(debug=self.debug, logger=self.logger, verbose=self.verbose, **credentials) as writer:
            writer.save_to_clickhouse(df)
            self.logger.debug("Save to ClickHouse completed.")

    def load_period(self, dt_field: str, start: str, end: str, **kwargs) -> Union[pd.DataFrame, dd.DataFrame]:
        """Synchronous convenience method for loading a date range."""
        final_kwargs = self._prepare_period_filters(dt_field, start, end, **kwargs)
        return self.load(**final_kwargs)

    async def aload_period(self, dt_field: str, start: str, end: str, **kwargs) -> Union[pd.DataFrame, dd.DataFrame]:
        """Asynchronous convenience method for loading a date range."""
        final_kwargs = self._prepare_period_filters(dt_field, start, end, **kwargs)
        return await self.aload(**final_kwargs)

    def _prepare_period_filters(self, dt_field: str, start: str, end: str, **kwargs) -> dict:
        start_date, end_date = pd.to_datetime(start).date(), pd.to_datetime(end).date()
        if start_date > end_date: raise ValueError("'start' date cannot be later than 'end' date.")
        field_map = self._backend_params.field_map or {}
        reverse_map = {v: k for k, v in field_map.items()} if field_map else {}
        if len(reverse_map) != len(field_map): self.logger.warning(
            "field_map values are not unique; reverse mapping may be unreliable.")
        mapped_field = reverse_map.get(dt_field, dt_field)
        if start_date == end_date:
            kwargs[f"{mapped_field}__date"] = start_date
        else:
            kwargs[f"{mapped_field}__date__range"] = [start_date, end_date]
        self.logger.debug(f"Period load generated filters: {kwargs}")
        return kwargs
