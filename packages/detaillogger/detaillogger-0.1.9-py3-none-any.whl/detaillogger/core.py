"""
core.py

DetailLogger: A logger for detailed tracebacks and caller info.

Author: Ryan LaPine
Date:   2025-07-30
Version:0.1.9
"""
from .detail_logger import DetailLogger
from typing import Optional

#wrapped functions for direct calls
detail_logger = None

def _get_logger(logging_level: int=None, log_file_name: str=None) -> None:
    global detail_logger
    if detail_logger is None:
        detail_logger = DetailLogger(file_name=log_file_name)
    return detail_logger

def log(message: str, logging_level: int=None, log_file_name: str=None) -> None:
    logger = _get_logger(logging_level, log_file_name)
    logger.log(message = message)

def log_exception(ex: BaseException, details: Optional[str] = None, logging_level: int = None, log_file_name: str = None) -> None:
    logger = _get_logger(logging_level, log_file_name)
    logger.log_exception(ex=ex, details=details)

def main() -> None:
    """
    Simple CLI for testing DetailLogger.
    """
    print()
    print()
    log_to_file = input("Also log to file? (y/n):").strip().lower() == 'y'
    file_name = None
    if log_to_file:
        file_name = input("Enter filname:")
    detail_logger = DetailLogger(file_name=file_name)
    print()
    print("Options")
    print("1) Log details.")
    print("2) Log 'division by zero' exception.")
    print("3) Log custom exception.")
    print("q) Exit.")
    option = input("Enter an option:").strip()
    print()
    match option:
        case '1':
            msg = input("Enter message to log:")
            detail_logger.log(msg)
            # log(msg)
            print("Message logged.")

        case '2':
            msg = input("Enter additional message to log with exception:")
            print("Raising 'division by zero' exception.")
            try:
                x = 1/0
            except Exception as ex:
                detail_logger.log_exception(ex, details=msg)
                # log_exception(ex=ex, details=msg)
            print("Exception logged.")
        case '3':
            ex_name = input("Enter custom exception name:")
            try:
                raise Exception(ex_name)
            except Exception as ex:
                detail_logger.log_exception(ex)
            print("Custom exception logged.")
    print()
    print()
if __name__ == "__main__":
    main()