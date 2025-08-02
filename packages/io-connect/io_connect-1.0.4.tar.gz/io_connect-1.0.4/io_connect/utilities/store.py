import sys
import logging
import asyncio
from timeit import default_timer
from typing import Optional


class Logger:
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        message: str = "",
        log_time: bool = False,
    ):
        self.interval = 0
        self.message = message
        self.log_time = log_time
        self.logger = logger

    def __enter__(self):
        self.start = default_timer()
        return self

    def __exit__(self, *args):
        self.end = default_timer()

        if self.log_time:
            self.interval = self.end - self.start
            self.info(f"[NETWORK] {self.message} {self.interval:.4f} seconds")

    async def __aenter__(self):
        self.start = default_timer()
        return self

    async def __aexit__(self, *args):
        self.end = default_timer()

        if self.log_time:
            self.interval = self.end - self.start
            await self.ainfo(f"[NETWORK] {self.message} {self.interval:.4f} seconds")

    def info(self, log: str):
        if self.logger:
            self.logger.info(log)
        else:
            print(log)

    def error(self, log: str):
        if self.logger:
            self.logger.error(log)
        else:
            print(log)

    async def ainfo(self, log: str):
        """Async version of info method to avoid blocking I/O operations."""
        if self.logger:
            # Run potentially blocking logger operation in thread pool
            await asyncio.to_thread(self.logger.info, log)
        else:
            # Run potentially blocking print operation in thread pool
            await asyncio.to_thread(print, log)

    async def aerror(self, log: str):
        """Async version of error method to avoid blocking I/O operations."""
        if self.logger:
            # Run potentially blocking logger operation in thread pool
            await asyncio.to_thread(self.logger.error, log)
        else:
            # Run potentially blocking print operation in thread pool
            await asyncio.to_thread(print, log)

    def display_log(self, log: str):
        """
        Display a log message on the console.

        This function writes a log message to the standard output stream (stdout),
        overwriting any existing content on the current line.

        Args:
            log (str): The log message to be displayed.

        Returns:
            None

        Example:
            >>> display_log("Processing...")  # Displays "Processing..." on the console

        """

        # Move the cursor to the beginning of the line
        sys.stdout.write("\r")

        # Clear the content from the cursor to the end of the line
        sys.stdout.write("\033[K")

        # Write the log message
        sys.stdout.write(log)

        # Flush the output buffer to ensure the message is displayed immediately
        sys.stdout.flush()

    async def adisplay_log(self, log: str):
        """
        Async version of display_log to avoid blocking stdout operations.
        
        Args:
            log (str): The log message to be displayed.
            
        Returns:
            None
        """
        def _display_log_sync():
            # Move the cursor to the beginning of the line
            sys.stdout.write("\r")
            # Clear the content from the cursor to the end of the line
            sys.stdout.write("\033[K")
            # Write the log message
            sys.stdout.write(log)
            # Flush the output buffer to ensure the message is displayed immediately
            sys.stdout.flush()
        
        # Run potentially blocking stdout operations in thread pool
        await asyncio.to_thread(_display_log_sync)


class AsyncLogger:
    """
    Dedicated async logger class for use in async contexts.
    Provides non-blocking logging operations using asyncio.to_thread.
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        message: str = "",
        log_time: bool = False,
    ):
        self.interval = 0
        self.message = message
        self.log_time = log_time
        self.logger = logger

    async def __aenter__(self):
        self.start = default_timer()
        return self

    async def __aexit__(self, *args):
        self.end = default_timer()

        if self.log_time:
            self.interval = self.end - self.start
            await self.info(f"[NETWORK] {self.message} {self.interval:.4f} seconds")

    async def info(self, log: str):
        """Async info logging method."""
        if self.logger:
            await asyncio.to_thread(self.logger.info, log)
        else:
            await asyncio.to_thread(print, log)

    async def error(self, log: str):
        """Async error logging method."""
        if self.logger:
            await asyncio.to_thread(self.logger.error, log)
        else:
            await asyncio.to_thread(print, log)

    async def display_log(self, log: str):
        """
        Async version of display_log for console output.
        
        Args:
            log (str): The log message to be displayed.
            
        Returns:
            None
        """
        def _display_log_sync():
            sys.stdout.write("\r")
            sys.stdout.write("\033[K")
            sys.stdout.write(log)
            sys.stdout.flush()
        
        await asyncio.to_thread(_display_log_sync)


def ERROR_MESSAGE(response, url):
    return f"""
[STATUS CODE] {response.status_code}
[URL] {url}
[SERVER INFO] {response.headers.get("Server", "Unknown Server")}
[RESPONSE] {response.text}
"""
