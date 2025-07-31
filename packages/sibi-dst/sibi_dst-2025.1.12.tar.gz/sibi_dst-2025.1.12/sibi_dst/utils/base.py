import asyncio
from .log_utils import Logger

class ManagedResource:
    """
    A base class providing context management for resources like loggers and filesystems.

    It handles the creation and cleanup of these resources, ensuring they are only
    closed if they were created by the instance itself.
    """

    def __init__(self, **kwargs):
        self.debug = kwargs.get("debug", False)
        self.verbose = kwargs.get("verbose", False)

        # --- Logger Management (Refactored) ---
        logger = kwargs.get("logger")
        if logger:
            # An existing logger instance was provided by the user
            self.logger = logger
            self._own_logger = False
            self.logger.debug(f"'{self.__class__.__name__}' is tapping into an existing logger.")
        else:
            # No pre-configured logger, so we will create and "own" a new one.
            self._own_logger = True
            logger_config = kwargs.get("logger_config", {})

            # Set default logger_name if not specified in the config
            logger_config.setdefault("logger_name", self.__class__.__name__)

            # Set log_level based on debug flag, but respect user-provided level
            default_level = Logger.DEBUG if self.debug else Logger.INFO
            logger_config.setdefault("log_level", default_level)

            # Create the logger using the provided or default configuration
            self.logger = Logger.default_logger(**logger_config)
            if self.logger:
                self.logger.debug(f"'{self.__class__.__name__}' is starting its own logger.")

        fs = kwargs.get("fs")
        self._own_fs = fs is None
        self.fs = fs or None # we want to allow None as a valid fs to trigger a failure if needed

        self._entered = False

    def __enter__(self):
        """Enter the runtime context."""
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and trigger cleanup."""
        self.cleanup()
        return False  # Propagate exceptions

    # --- Asynchronous Context Management ---

    async def __aenter__(self):
        """Enter the runtime context for 'async with' statements."""
        self._entered = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and trigger cleanup for 'async with' statements."""
        await self.acleanup()
        return False  # Propagate exceptions

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the ManagedResource."""
        # Dynamically get the name of the class or subclass
        class_name = self.__class__.__name__

        # Determine the status of the logger and filesystem
        logger_status = "own" if self._own_logger else "external"
        fs_status = "own" if self._own_fs else "external"

        return (
            f"<{class_name} debug={self.debug}, "
            f"logger='{logger_status}', fs='{fs_status}'>"
        )

    def cleanup(self):
        """
        Cleanup resources managed by this instance.
        """
        if self._own_fs and hasattr(self.fs, "clear_instance_cache"):
            if self.logger:
                self.logger.debug(f"'{self.__class__.__name__}' is clearing its own filesystem cache.")
            self.fs.clear_instance_cache()

        if self._own_logger and hasattr(self.logger, "shutdown"):
            # Ensure the logger exists before trying to use or shut it down
            if self.logger:
                self.logger.debug(f"'{self.__class__.__name__}' is shutting down its own logger.")
                self.logger.shutdown()
            self.logger = None  # Set to None after shutdown

        self._entered = False

    async def acleanup(self):
        """
        Async Cleanup resources managed by this instance.
        """
        if self._own_fs and hasattr(self.fs, "clear_instance_cache"):
            if self.logger:
                self.logger.debug(f"'{self.__class__.__name__}' is clearing its own filesystem cache.")
            self.fs.clear_instance_cache()

        if self._own_logger and hasattr(self.logger, "shutdown"):
            # Ensure the logger exists before trying to use or shut it down
            if self.logger:
                self.logger.debug(f"'{self.__class__.__name__}' is shutting down its own logger.")
                self.logger.shutdown()
            self.logger = None  # Set to None after shutdown

        self._entered = False

