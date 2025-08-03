"""
detail_logger.py

DetailLogger: A logger for detailed tracebacks and caller info.

Author: Ryan LaPine
Date:   2025-07-30
Version:0.1.9
"""

import logging
import traceback
import inspect
from dataclasses import dataclass
from typing import Optional
import getpass
import os


class DetailLogger:
    """
    Logger that captures detailed messages, context, and exceptions with caller info.
    """
    # default string length to fill tab
    FILL = 16

    ALLOWED_LEVELS = [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ]
    DEFAULT_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DEFAULT_LOG_FILE = "detaillogger.log"

    def __init__(
        self,
        level: int = logging.DEBUG,
        fmt: str = DEFAULT_FORMAT,
        file_name: Optional[str] = None,
    ) -> None:
        """
        Initialize DetailLogger.

        Args:
            level:   Logging level (DEBUG, INFO, etc.).
            fmt:     Log message format string.
            file_name: Optional path to a file for log output.
        """
        # Base logger always set to DEBUG; handlers filter their own levels
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Validate level or default to DEBUG
        self.level = level if level in self.ALLOWED_LEVELS else logging.DEBUG

        # File handler (if requested)
        if file_name:
            fh = logging.FileHandler(file_name)
            fh.setLevel(self.level)
            fh.setFormatter(logging.Formatter(fmt))
            self.logger.addHandler(fh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(self.level)
        ch.setFormatter(logging.Formatter(fmt))
        self.logger.addHandler(ch)

        # Select appropriate logging method
        self.log_function = {
            logging.DEBUG: self.logger.debug,
            logging.INFO: self.logger.info,
            logging.WARNING: self.logger.warning,
            logging.ERROR: self.logger.error,
            logging.CRITICAL: self.logger.critical,
        }.get(self.level, self.logger.debug)

    @dataclass
    class Caller:
        """
        Data class storing context of the caller.
        """
        full_path: str
        file_name: str
        function_name: str
        line_num: int
        user_name: str
        
    def _get_caller(self) -> Caller:
        """
        Walk the stack to identify who called the logging method.

        Returns:
            Caller: context of the calling frame.
        """
        frame = inspect.currentframe()
        # f_back: _get_caller → _log_base → the real caller
        caller_frame = frame.f_back.f_back.f_back  # type: ignore
        
        info = inspect.getframeinfo(caller_frame)
        user_name = getpass.getuser()
        
        return self.Caller(
            full_path=info.filename,
            file_name=info.filename,
            function_name=info.function,
            line_num=info.lineno,
            user_name=user_name,
        )

    def _log_base(self, details:str) -> None:
        caller = self._get_caller()
        self.log_function(f"{"Details:".ljust(self.FILL, ' ')}{details}")
        file_name = os.path.basename(caller.file_name)
        self.log_function(f"{"File:".ljust(self.FILL, ' ')}{file_name}")
        self.log_function(f"{"Function:".ljust(self.FILL, ' ')}{caller.function_name}()")
        self.log_function(f"{"Line:".ljust(self.FILL, ' ')}{caller.line_num}")
        self.log_function(f"{"User:".ljust(self.FILL, ' ')}{caller.user_name}\n")   

    def log(self, message: str) -> None:
        """
        Log a custom message along with caller info.

        Args:
            message: The detail message to record.
        """
        self.log_function("MESSAGE")
        self._log_base(message)
         

    def log_exception(self, ex: BaseException, details: Optional[str] = None) -> None:
        """
        Log an exception with traceback and caller context.

        Args:
            ex:      The exception instance.
            details: Extra information to include.
        """
        self.log_function(f"EXCEPTION")
        
        # handle common syntax error of just sending message and not the exception object
        if not isinstance(ex, BaseException):
            self.log_function(f"{"Type:".ljust(self.FILL, ' ')}Not Sent")
            self.log_function(f"{"Message:".ljust(self.FILL, ' ')}Not Sent")
            # try to case ex to str
            try:
                missing_ex_message = str(ex)
            except:
                missing_ex_message = f"Unable to cast '{ex}' to string."
        
            self._log_base(details = missing_ex_message)
            
        # an exception object was sent in
        else:
            self.log_function(f"{"Type:".ljust(self.FILL, ' ')}{type(ex).__name__}")
            self.log_function(f"{"Message:".ljust(self.FILL, ' ')}{ex}")

            if details is not None:
                self.log_function(f"{"Details:".ljust(self.FILL, ' ')}{details}")
            
            # view traceback info if exception was actually thrown
            if ex.__traceback__ is not None:
                tb = traceback.extract_tb(ex.__traceback__)
                
                if tb is not None and len(tb) > 0:
                    # print info where exception was thrown
                    ex_line = tb[-1]
                    file_name = os.path.basename(ex_line.filename)
                    self.log_function(f"{"From:".ljust(self.FILL, ' ')}{ex_line.name}()")
                    self.log_function(f"{"File:".ljust(self.FILL, ' ')}{file_name}")
                    self.log_function(f"{"Line:".ljust(self.FILL, ' ')}{ex_line.lineno}")
                    self.log_function(f"{"Code:".ljust(self.FILL, ' ')}{ex_line.line}")
                    
                    # print stack info for all but main execption entry
                    # for i, tb_entry in enumerate(reversed(tb[1:])):
                    if len(tb) > 1:
                        for i, tb_entry in enumerate(tb):
                            self.log_function("---------------------------------------------")
                            self.log_function(f"Traceback({i + 1})")
                            file_name = os.path.basename(tb_entry.filename)
                            self.log_function(f"{"From:".ljust(self.FILL, ' ')}{tb_entry.name}()")
                            self.log_function(f"{"File:".ljust(self.FILL, ' ')}{file_name}")
                            self.log_function(f"{"Line:".ljust(self.FILL, ' ')}{tb_entry.lineno}")
                            self.log_function(f"{"Code:".ljust(self.FILL, ' ')}{tb_entry.line}")
                self.log_function("---------------------------------------------")
            # exception was not thrown so no traceback available get info from caller
            else:
                caller = self._get_caller()
                self.log_function(f"{"From:".ljust(self.FILL, ' ')}{caller.function_name}()")
                file_name = os.path.basename(caller.file_name)
                self.log_function(f"{"File:".ljust(self.FILL, ' ')}{file_name}")
                self.log_function(f"{"Line:".ljust(self.FILL, ' ')}{caller.line_num}") 
            # log caller user info
            caller = self._get_caller()
            self.log_function(f"{"User:".ljust(self.FILL, ' ')}{caller.user_name}\n")  
                

"""
Console Test
"""

def throw_div_zero():
    x = 1/0

def throw_value_error():
    int("Value Error")

def throw_index_error():
    a_list=[]
    x = a_list[1]

def main():
    """
    Runs samples of all methods in DetailLogger
    """

    # level set at DEBUG
    # set filname if you want to log to file
    # log_file_name = "logfile.log"
    log_file_name = None
    detail_logger = DetailLogger(level=logging.DEBUG,file_name=log_file_name)
    detail_logger.log("Test of DetailLogger")
    detail_logger.log_exception(Exception("Test Exception Not Thrown"))
    detail_logger.log_exception("this is a common syntax error of sending a message and no exception")
    
    try:
        throw_div_zero()
    except Exception as ex:
        detail_logger.log_exception(ex=ex, details="Additional Info about Div by Zero Test")

    try:
        throw_value_error()
    except Exception as ex:
        detail_logger.log_exception(ex=ex, details="Additional Info about Value Error Test")

    try:
        throw_index_error()
    except Exception as ex:
        detail_logger.log_exception(ex=ex, details="Additional Info about Index Error Test")

if __name__=="__main__":
    main()