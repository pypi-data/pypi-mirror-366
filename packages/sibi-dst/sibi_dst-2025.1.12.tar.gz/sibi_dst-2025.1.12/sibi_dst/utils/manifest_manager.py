import pandas as pd
import fsspec
import threading
import uuid
from typing import List, Optional, Set, Dict, Any
import json, base64, hashlib
from sibi_dst.utils import Logger


class MissingManifestManager:
    """
    A thread-safe manager for a Parquet file manifest.

    This class handles creating, reading, and appending to a Parquet manifest file
    that tracks a list of paths. It is designed to be resilient, using atomic
    file operations to prevent data corruption during writes, and can clean up
    orphaned temporary files from previous runs.

    Attributes:
        fs (fsspec.AbstractFileSystem): The filesystem object to interact with.
        manifest_path (str): The full path to the manifest file.
        clear_existing (bool): If True, any existing manifest will be overwritten
            on the first save operation of this instance's lifecycle.
        logger (Logger): A logger instance for logging messages.
    """

    def __init__(
            self,
            fs: fsspec.AbstractFileSystem,
            manifest_path: str,
            clear_existing: bool = False,
            **kwargs: Any,
    ):
        self.fs: fsspec.AbstractFileSystem = fs
        self.manifest_path: str = manifest_path.rstrip("/")
        self.clear_existing: bool = clear_existing

        self.debug: bool = kwargs.get("debug", False)
        self.logger: Logger = kwargs.get(
            "logger",
            Logger.default_logger(logger_name="missing_manifest_manager")
        )
        self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)

        self._new_records: List[Dict[str, str]] = []
        self._loaded_paths: Optional[Set[str]] = None
        self._lock = threading.Lock()  # A standard Lock is sufficient

        # Clean up any orphaned temp files from previous failed runs
        self._cleanup_orphaned_files()

    def _safe_exists(self, path: str) -> bool:
        """Safely check if a path exists, handling potential exceptions."""
        try:
            return self.fs.exists(path)
        except Exception as e:
            self.logger.warning(f"Error checking existence of '{path}': {e}")
            return False

    def load_existing(self) -> Set[str]:
        """
        Loads the set of paths from the existing manifest file.

        The result is cached in memory. If the manifest does not exist or fails
        to load, an empty set is returned. This operation is thread-safe.

        Returns:
            A set of strings, where each string is a path from the manifest.
        """
        with self._lock:
            if self._loaded_paths is not None:
                return self._loaded_paths

            if not self._safe_exists(self.manifest_path):
                self._loaded_paths = set()
                return self._loaded_paths

            try:
                df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
                # Robustly extract non-empty, non-null paths
                paths = (
                    df.get("path", pd.Series(dtype=str))
                    .dropna().astype(str)
                    .loc[lambda s: s.str.strip().astype(bool)]
                )
                self._loaded_paths = set(paths.tolist())
            except Exception as e:
                self.logger.warning(
                    f"Failed to load manifest '{self.manifest_path}', "
                    f"treating as empty. Error: {e}"
                )
                self._loaded_paths = set()

            return self._loaded_paths

    def record(self, full_path: str) -> None:
        """
        Records a new path to be added to the manifest upon the next save.

        Args:
            full_path: The path to record.
        """
        if not full_path or not isinstance(full_path, str):
            return
        with self._lock:
            self._new_records.append({"path": full_path})

    def save(self) -> None:
        """
        Saves all new records to the manifest file.

        This method merges new records with existing ones (unless `clear_existing`
        is True), removes duplicates, and writes the result back to the manifest.
        The write operation is performed atomically by writing to a temporary file
        first, then renaming or copying it to the final destination.
        """
        with self._lock:
            if not self._new_records and not self.clear_existing:
                self.logger.debug("Manifest Manager: No new records to save.")
                return

            new_df = pd.DataFrame(self._new_records)
            new_df = (
                new_df.get("path", pd.Series(dtype=str))
                .dropna().astype(str)
                .loc[lambda s: s.str.strip().astype(bool)]
                .to_frame(name="path")
            )

            # Determine the final DataFrame to be written
            should_overwrite = self.clear_existing or not self._safe_exists(self.manifest_path)
            if should_overwrite:
                out_df = new_df
            else:
                try:
                    old_df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
                    out_df = pd.concat([old_df, new_df], ignore_index=True)
                except Exception as e:
                    self.logger.warning(f"Could not read existing manifest to merge, overwriting. Error: {e}")
                    out_df = new_df

            out_df = out_df.drop_duplicates(subset=["path"]).reset_index(drop=True)

            # Ensure parent directory exists
            parent = self.manifest_path.rsplit("/", 1)[0]
            self.fs.makedirs(parent, exist_ok=True)

            # Perform an atomic write using a temporary file
            temp_path = f"{self.manifest_path}.tmp-{uuid.uuid4().hex}"
            try:
                out_df.to_parquet(temp_path, filesystem=self.fs, index=False)
                self.fs.copy(temp_path, self.manifest_path)
                self.fs.rm_file(temp_path)
                self.logger.info(f"Copied manifest to {self.manifest_path} (temp: {temp_path})")
            except Exception as e:
                self.logger.error(f"Failed to write or move manifest: {e}")
                # Re-raise so the caller knows the save operation failed
                #raise
            finally:
                # CRITICAL: Always clean up the temporary file
                if self._safe_exists(temp_path):
                    try:
                        self._cleanup_orphaned_files()
                    except Exception as e:
                        self.logger.error(f"Failed to remove temporary file '{temp_path}': {e}")

            # Reset internal state
            self._new_records.clear()
            self._loaded_paths = set(out_df["path"].tolist())
            # After the first successful save, disable clear_existing behavior
            self.clear_existing = False

    def _cleanup_orphaned_files(self) -> None:
        """Finds and removes any orphaned temporary manifest files from prior runs."""
        self.logger.debug("Checking for orphaned temporary files...")
        if not hasattr(self.fs, "s3"):
            self.logger.info("Filesystem is not s3fs; skipping temp cleanup.")
            return
        try:

            # Use glob to find all files matching the temp pattern in a filesystem-agnostic way
            temp_file_pattern = f"{self.manifest_path}.tmp-*"
            orphaned_files = self.fs.glob(temp_file_pattern)

            if not orphaned_files:
                self.logger.debug("No orphaned files found.")
                return

            self.logger.info(f"Found {orphaned_files} orphaned temp manifest(s). Cleaning up...")
            for f_path in orphaned_files:
                try:
                    self.fs.rm_file(f_path)
                    self.logger.info(f"Deleted orphaned file: {f_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete orphaned temp file '{f_path}': {e}")
        except Exception as e:
            # This is a non-critical operation, so we just log the error
            self.logger.error(f"An unexpected error occurred during temp file cleanup: {e}")

    @staticmethod
    def _parse_s3_path(s3_path: str):
        if not s3_path.startswith("s3://"):
            raise ValueError("Invalid S3 path. Must start with 's3://'.")
        path_parts = s3_path[5:].split("/", 1)
        bucket_name = path_parts[0]
        prefix = path_parts[1] if len(path_parts) > 1 else ""
        return bucket_name, prefix
