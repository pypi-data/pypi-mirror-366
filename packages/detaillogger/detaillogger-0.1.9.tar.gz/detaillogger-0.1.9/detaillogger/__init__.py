# detaillogger/__init__.py

"""
DetailLogger Package

DetailLogger is a lightweight Python utility for enhanced logging and exception tracing. 
It automatically captures contextual information—such as file name, function, 
and line number—whenever messages or exceptions are logged. 
Ideal for debugging, monitoring, and building maintainable systems.
"""

__version__ = "0.1.9"

from .core import log, log_exception
