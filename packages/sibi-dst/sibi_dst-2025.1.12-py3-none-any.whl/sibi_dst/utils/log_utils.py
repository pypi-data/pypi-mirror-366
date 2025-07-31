from __future__ import annotations
import logging
import os
import sys
import time
from logging import LoggerAdapter
from typing import Optional
from logging.handlers import RotatingFileHandler

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Tracer, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


class Logger:
    """
    Handles the creation and management of logging, with optional OpenTelemetry integration.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(
            self,
            log_dir: str,
            logger_name: str,
            log_file: str,
            log_level: int = logging.DEBUG,
            enable_otel: bool = False,
            otel_service_name: Optional[str] = None,
            otel_stream_name: Optional[str] = None,
            otel_endpoint: str = "0.0.0.0:4317",
            otel_insecure: bool = False,
    ):
        self.log_dir = log_dir
        self.logger_name = logger_name
        self.log_file = log_file
        self.log_level = log_level
        self.enable_otel = enable_otel
        self.otel_service_name = otel_service_name or self.logger_name
        self.otel_stream_name = otel_stream_name
        self.otel_endpoint = otel_endpoint
        self.otel_insecure = otel_insecure
        self.logger_provider: Optional[LoggerProvider] = None
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[Tracer] = None

        # Internal logger for configuration vs. public logger for use
        self._core_logger: Optional[logging.Logger] = logging.getLogger(self.logger_name)
        self.logger: Optional[logging.Logger | LoggerAdapter] = self._core_logger

        self._setup()

    def _setup(self):
        """Set up the logger and then wrap it in an adapter if needed."""
        # 1. Create and configure the actual logger instance
        self._core_logger = logging.getLogger(self.logger_name)
        self._core_logger.setLevel(self.log_level)
        self._core_logger.propagate = False

        # 2. Add all handlers to the actual logger instance
        self._setup_standard_handlers()
        if self.enable_otel:
            self._setup_otel_handler()

        # 3. Create the final, public-facing logger object
        if self.enable_otel and self.otel_stream_name:
            # If stream name is used, wrap the configured logger in an adapter
            attributes = {"attributes": {
                "log_stream": self.otel_stream_name,
                "log_service_name": self.otel_service_name,
                "logger_name": self.logger_name,
                }
            }
            self.logger = LoggerAdapter(self._core_logger, extra=attributes)
        else:
            # Otherwise, just use the logger directly
            self.logger = self._core_logger

    def _setup_standard_handlers(self):
        """Sets up the file and console logging handlers."""
        os.makedirs(self.log_dir, exist_ok=True)
        calling_script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        log_file_path = os.path.join(
            self.log_dir, f"{self.log_file}_{calling_script}.log"
        )

        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        #formatter.converter = time.localtime
        formatter.converter = time.gmtime  # Use GMT for consistency in logs

        #file_handler = logging.FileHandler(log_file_path, delay=True)
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5, delay=True)
        file_handler.setFormatter(formatter)
        self._core_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._core_logger.addHandler(console_handler)

    def _setup_otel_handler(self):
        """Sets up the OpenTelemetry logging handler."""
        resource = Resource.create({"service.name": self.otel_stream_name or self.otel_service_name})
        self.logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(self.logger_provider)
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)

        exporter = OTLPLogExporter(
            endpoint=self.otel_endpoint, insecure=self.otel_insecure
        )
        log_processor = BatchLogRecordProcessor(exporter)
        self.logger_provider.add_log_record_processor(log_processor)

        span_exporter = OTLPSpanExporter(
            endpoint=self.otel_endpoint, insecure=self.otel_insecure
        )
        span_processor = BatchSpanProcessor(span_exporter)
        self.tracer_provider.add_span_processor(span_processor)
        self.tracer = trace.get_tracer(
            self.logger_name, tracer_provider=self.tracer_provider
        )
        otel_handler = LoggingHandler(
            level=logging.NOTSET, logger_provider=self.logger_provider
        )
        self._core_logger.addHandler(otel_handler)
        self._core_logger.info("OpenTelemetry logging and tracing enabled and attached.")

    @classmethod
    def default_logger(
            cls,
            log_dir: str = './logs/',
            logger_name: Optional[str] = None,
            log_file: Optional[str] = None,
            log_level: int = logging.INFO,
            enable_otel: bool = False,
            otel_service_name: Optional[str] = None,
            otel_stream_name: Optional[str] = None,
            otel_endpoint: str = "0.0.0.0:4317",
            otel_insecure: bool = False,
    ) -> 'Logger':
        try:
            frame = sys._getframe(1)
            caller_name = frame.f_globals.get('__name__', 'default_logger')
        except (AttributeError, ValueError):
            caller_name = 'default_logger'

        logger_name = logger_name or caller_name
        log_file = log_file or logger_name

        return cls(
            log_dir=log_dir,
            logger_name=logger_name,
            log_file=log_file,
            log_level=log_level,
            enable_otel=enable_otel,
            otel_service_name=otel_service_name,
            otel_stream_name=otel_stream_name,
            otel_endpoint=otel_endpoint,
            otel_insecure=otel_insecure,
        )

    def shutdown(self):
        """Gracefully shuts down the logger and the OpenTelemetry provider."""
        if self.enable_otel and self.logger_provider:
            self.logger.info("Shutting down OpenTelemetry logger provider...")
            if self.otel_stream_name:
                self._core_logger.info(f"OpenObserve stream configured as: '{self.otel_stream_name}'")
            self.logger_provider.shutdown()
            print("Logger provider shut down.")
        logging.shutdown()

    def set_level(self, level: int):
        """Set the logging level for the logger."""
        self._core_logger.setLevel(level)

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def start_span(self, name: str, attributes: Optional[dict] = None):
        """
        Starts a span using the configured tracer.
        Usage:
            with logger.start_span("my-task") as span:
                ...
        """
        if not self.enable_otel or not self.tracer:
            self.warning("Tracing is disabled or not initialized. Cannot start span.")
            # return dummy context manager
            from contextlib import nullcontext
            return nullcontext()

        return self.tracer.start_as_current_span(name)

    # Use this decorator to trace a function
    def trace_function(self, span_name: Optional[str] = None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                name = span_name or func.__name__
                with self.start_span(name):
                    return func(*args, **kwargs)

            return wrapper

        return decorator


# import logging
# import os
# import sys
# import time
# from typing import Optional
#
#
# class Logger:
#     """
#     Handles the creation, setup, and management of logging functionalities.
#
#     This class facilitates logging by creating and managing a logger instance with
#     customizable logging directory, name, and file. It ensures logs from a script
#     are stored in a well-defined directory and file, and provides various logging
#     methods for different log levels. The logger automatically formats and handles
#     log messages. Additionally, this class provides a class method to initialize a
#     logger with default behaviors.
#
#     :ivar log_dir: Path to the directory where log files are stored.
#     :type log_dir: str
#     :ivar logger_name: Name of the logger instance.
#     :type logger_name: str
#     :ivar log_file: Base name of the log file.
#     :type log_file: str
#     :ivar logger: The initialized logger instance used for logging messages.
#     :type logger: logging.Logger
#     """
#
#     DEBUG = logging.DEBUG
#     INFO = logging.INFO
#     WARNING = logging.WARNING
#     ERROR = logging.ERROR
#     CRITICAL = logging.CRITICAL
#
#     def __init__(self, log_dir: str, logger_name: str, log_file: str, log_level: int = logging.DEBUG):
#         """
#         Initialize the Logger instance.
#
#         :param log_dir: Directory where logs are stored.
#         :param logger_name: Name of the logger instance.
#         :param log_file: Base name of the log file.
#         :param log_level: Logging level (defaults to DEBUG).
#         """
#         self.log_dir = log_dir
#         self.logger_name = logger_name
#         self.log_file = log_file
#         self.log_level = log_level
#         self.logger = None
#
#         self._setup()
#
#     def _setup(self):
#         """Set up the logger with file and console handlers."""
#         # Ensure the log directory exists
#         os.makedirs(self.log_dir, exist_ok=True)
#
#         # Get the name of the calling script
#         calling_script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
#
#         # Create a log file path
#         log_file_path = os.path.join(self.log_dir, f"{self.log_file}_{calling_script}.log")
#
#         # Delete the existing log file if it exists
#         if os.path.exists(log_file_path):
#             os.remove(log_file_path)
#
#         # Create a logger
#         self.logger = logging.getLogger(self.logger_name)
#         self.logger.setLevel(self.log_level)
#
#         # Create a formatter
#         formatter = logging.Formatter(
#             '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
#             datefmt='%Y-%m-%d %H:%M:%S'
#         )
#
#         formatter.converter = time.localtime  # << Set local time explicitly
#
#         # Create a file handler
#         file_handler = logging.FileHandler(log_file_path, delay=True)
#         file_handler.setFormatter(formatter)
#         self.logger.addHandler(file_handler)
#
#         # Create a console handler (optional)
#         console_handler = logging.StreamHandler()
#         console_handler.setFormatter(formatter)
#         self.logger.addHandler(console_handler)
#
#     @classmethod
#     def default_logger(
#             cls,
#             log_dir: str = './logs/',
#             logger_name: Optional[str] = None,
#             log_file: Optional[str] = None,
#             log_level: int = logging.INFO
#     ) -> 'Logger':
#         """
#         Class-level method to create a default logger with generic parameters.
#
#         :param log_dir: Directory where logs are stored (defaults to './logs/').
#         :param logger_name: Name of the logger (defaults to __name__).
#         :param log_file: Name of the log file (defaults to logger_name).
#         :param log_level: Logging level (defaults to INFO).
#         :return: Instance of Logger.
#         """
#         logger_name = logger_name or __name__
#         log_file = log_file or logger_name
#         return cls(log_dir=log_dir, logger_name=logger_name, log_file=log_file, log_level=log_level)
#
#     def set_level(self, level: int):
#         """
#         Set the logging level for the logger.
#
#         :param level: Logging level (e.g., logging.DEBUG, logging.INFO).
#         """
#         self.logger.setLevel(level)
#
#     def debug(self, msg: str, *args, **kwargs):
#         """Log a debug message."""
#         self.logger.debug(msg, *args, **kwargs)
#
#     def info(self, msg: str, *args, **kwargs):
#         """Log an info message."""
#         self.logger.info(msg, *args, **kwargs)
#
#     def warning(self, msg: str, *args, **kwargs):
#         """Log a warning message."""
#         self.logger.warning(msg, *args, **kwargs)
#
#     def error(self, msg: str, *args, **kwargs):
#         """
#         Log an error message.
#
#         To log exception information, use the `exc_info=True` keyword argument.
#         """
#         self.logger.error(msg, *args, **kwargs)
#
#     def critical(self, msg: str, *args, **kwargs):
#         """Log a critical message."""
#         self.logger.critical(msg, *args, **kwargs)
