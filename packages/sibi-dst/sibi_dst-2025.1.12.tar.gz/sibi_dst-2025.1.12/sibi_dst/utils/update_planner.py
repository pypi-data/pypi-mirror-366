import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Union, Tuple, Set, Iterator, ClassVar
import pandas as pd
from .date_utils import FileAgeChecker
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table

from sibi_dst.utils import ManagedResource


class UpdateConfig(BaseModel):
    """
    A unified Pydantic model for the data update process configuration.
    Acts as a single source of truth for all settings.
    """
    overwrite: bool = False
    reverse_order: bool = True
    ignore_missing: bool = False
    history_days_threshold: int = 30
    max_age_minutes: int = 1440  # 24 hours
    show_progress: bool = False
    verbose: bool = False
    debug: bool = False
    start_date: datetime.date
    end_date: datetime.date
    custom_priority_map: Optional[Dict[str, int]] = None
    max_threads: int = 3
    timeout: float = 30.0

    class Config:
        arbitrary_types_allowed = True

class UpdatePlanner(ManagedResource):
    """
    A utility class to scan a date-partitioned filesystem and
    generate an update plan indicating which dates need processing.

    Attributes:
        data_path:             Base path (always ends with '/').
        filename:              Filename inside each date folder.
        fs:                    fsspec filesystem instance.
        age_checker:           FileAgeChecker for computing file ages.
        reference_date:        The "today" date used for history windows (date or ISO string).
        history_days_threshold: Number of days considered "in history".
        max_age_minutes:       File staleness threshold in minutes.
        overwrite:             If True, forces updates for all dates.
        ignore_missing:        If True, skips missing files outside history.
        reverse_order:         If True, sorts dates descending in output.
        show_progress:         If True, displays a tqdm progress bar.
        logger:                Logger for informational messages.

    Note:
        generate_plan() will overwrite self.plan and self.df_req, and returns a DataFrame of required updates.
    """

    DEFAULT_PRIORITY_MAP: ClassVar[Dict[str, int]]={
        "file_is_recent": 0,
        "missing_ignored": 0,
        "overwrite_forced": 1,
        "create_missing": 2,
        "missing_in_history": 3,
        "stale_in_history": 4,
    }

    DEFAULT_MAX_AGE_MINUTES: int = 1440
    DEFAULT_HISTORY_DAYS_THRESHOLD: int = 30

    def __init__(
            self,
            data_path: str,
            filename: str,
            description: str = "Update Planner",
            reference_date: Union[str, datetime.date] = None,
            history_days_threshold: int = DEFAULT_HISTORY_DAYS_THRESHOLD,
            max_age_minutes: int = DEFAULT_MAX_AGE_MINUTES,
            overwrite: bool = False,
            ignore_missing: bool = False,
            custom_priority_map: Optional[Dict[str, int]] = None,
            reverse_order: bool = False,
            show_progress: bool = False,
            skipped: Optional[List[str]] = None,
            **kwargs
    ):
        # Initialize state
        super().__init__(**kwargs)
        self.plan: pd.DataFrame = pd.DataFrame()
        self.df_req: pd.DataFrame = pd.DataFrame()
        self.description = description
        self.data_path = self._ensure_trailing_slash(data_path)
        self.filename = filename
        self.reverse_order = reverse_order
        self.show_progress = show_progress
        self.age_checker = FileAgeChecker(debug=self.debug, logger=self.logger)

        # Normalize reference date
        if reference_date is None:
            self.reference_date = datetime.date.today()
        else:
            self.reference_date = pd.to_datetime(reference_date).date()

        # Thresholds and flags
        self.history_days_threshold = history_days_threshold
        self.max_age_minutes = max_age_minutes
        self.overwrite = overwrite
        self.ignore_missing = ignore_missing
        self.priority_map = custom_priority_map or self.DEFAULT_PRIORITY_MAP
        self.skipped = skipped or []

    @staticmethod
    def _ensure_trailing_slash(path: str) -> str:
        """Ensure that the provided path ends with a single '/'."""
        return path.rstrip('/') + '/'

    def _generate_plan(
            self,
            start: datetime.date,
            end: datetime.date,
            freq: str = "D"
    ) -> None:
        """
        Internal: populates self.plan with all dates, and self.df_req with only those needing update.
        """
        dates = pd.date_range(start=start, end=end, freq=freq).date.tolist()
        history_start = self.reference_date - datetime.timedelta(days=self.history_days_threshold)
        rows: List[Dict] = []

        # Parallel file status checks
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._get_file_status, d): d for d in dates}
            iterator = as_completed(futures)
            if self.show_progress:
                from tqdm import tqdm
                iterator = tqdm(
                    iterator,
                    total=len(futures),
                    desc=f"Scanning dates for {self.description}",
                    unit="date",
                    leave=False
                )
            for future in iterator:
                d = futures[future]
                try:
                    exists, age = future.result()
                    rows.append(self._make_row(d, history_start, exists, age))
                except Exception as exc:
                    self.logger.error(f"Error processing date {d}: {exc}")
                    rows.append(self._make_row(d, history_start, False, None))

        df = pd.DataFrame(rows)
        df = df.sort_values(
            by=["update_priority", "date"],
            ascending=[True, not self.reverse_order]
        ).reset_index(drop=True)

        self.plan = df
        self.df_req = df[df.update_required].copy()

    def generate_plan(
            self,
            start: Union[str, datetime.date],
            end: Union[str, datetime.date]
    ) -> pd.DataFrame:
        """
        Generate and return a DataFrame of dates requiring updates between start and end,
        sorted by update_priority and date (descending if reverse_order=True).
        """
        sd = pd.to_datetime(start).date()
        ed = pd.to_datetime(end).date()
        if sd > ed:
            raise ValueError(f"Start date ({sd}) must be on or before end date ({ed}).")

        self.logger.info(f"Generating update plan for {self.description} from {sd} to {ed}")
        self._generate_plan(sd, ed)
        self.logger.info(
            f"Plan built for {self.description}: {len(self.plan)} dates evaluated, "
            f"{len(self.df_req)} require update"
        )

        return self.df_req

    def show_update_plan(self) -> None:
        """
        Display the full update plan as a styled DataFrame.
        """
        if self.plan.empty:
            self.logger.warning("No update plan available. Call generate_plan() first.")
            return

        console = Console(record=True)

        table = Table(title=f"Update Plan for {self.data_path}", show_header=True, header_style="bold magenta")
        for column in self.plan.columns:
            table.add_column(column, justify="left")
        for _, row in self.plan.iterrows():
            table.add_row(*(str(item) for item in row))

        console = Console()
        with console.capture() as capture:
            console.print(table)
        plan_string = capture.get()

        self.logger.info(f"Full Update Plan:\n{plan_string.strip()}")

    def get_tasks_by_priority(self) -> Iterator[Tuple[int, List[datetime.date]]]:
        """Yields batches of dates to be processed, grouped and sorted by priority."""
        if self.plan.empty:
            return

        required_updates = self.plan[self.plan['update_required']].copy()
        if required_updates.empty:
            return

        for priority in sorted(required_updates["update_priority"].unique()):
            dates_df = required_updates[required_updates["update_priority"] == priority]
            # Sort dates within the priority group
            sorted_dates = dates_df.sort_values(by=["date"], ascending=not self.reverse_order)
            dates = sorted_dates["date"].tolist()
            if dates:
                yield priority, dates

    def _get_file_status(
            self,
            date: datetime.date
    ) -> Tuple[bool, Optional[float]]:
        """
        Check file existence and age for the given date.
        """
        just_path = f"{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/"
        if just_path in self.skipped:
            self.logger.debug(f"Update plan is skipping date {date} as it is in the skipped list.")
            return False, None
        path = f"{just_path}{self.filename}"
        try:
            exists = self.fs.exists(path)
            age = self.age_checker.get_file_or_dir_age_minutes(path, self.fs) if exists else None
            return exists, age
        except Exception:
            return False, None

    def _make_row(
            self,
            date: datetime.date,
            history_start: datetime.date,
            file_exists: bool,
            file_age: Optional[float]
    ) -> Dict:
        """
        Build a single plan row based on flags and thresholds.
        """
        within_history = history_start <= date <= self.reference_date
        update_required = False

        # 1. Overwrite mode forces update
        if self.overwrite:
            category = "overwrite_forced"
            update_required = True
        # 2. Within history window: missing or stale
        elif within_history:
            if not file_exists:
                category = "missing_in_history"
                update_required = True
            elif file_age is not None and file_age > self.max_age_minutes:
                category = "stale_in_history"
                update_required = True
            else:
                category = "file_is_recent"
        # 3. Outside history, missing file
        elif not file_exists and not self.ignore_missing:
            category = "create_missing"
            update_required = True
        # 4. Everything else (existing files outside history, or ignored missing)
        else:
            category = "missing_ignored" if not file_exists else "file_is_recent"

        return {
            "date": date,
            "file_exists": file_exists,
            "file_age_minutes": file_age,
            "update_category": category,
            "update_priority": self.priority_map.get(category, 99),
            "update_required": update_required,
            "description": self.description,
        }

    def exclude_dates(self, dates: Set[datetime.date]) -> None:
        """
        Exclude specific dates from the update plan.
        """
        if not isinstance(dates, set):
            raise ValueError("dates must be a set of datetime.date objects.")
        if self.plan.empty:
            self.logger.warning("No update plan available. Call generate_plan() first.")
            return
        self.plan = self.plan[~self.plan['date'].isin(dates)]
        self.df_req = self.plan[self.plan["update_required"]]
        self.logger.info(f"Excluded {len(dates)} dates from the update plan.")
