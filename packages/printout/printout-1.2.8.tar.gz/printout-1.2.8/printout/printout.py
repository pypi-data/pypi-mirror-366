import os
from pathlib import Path
import sys
from datetime import datetime

def printout(*args, filename=None, directory=None, **kwargs):
    """
    A print function that also logs output to a file.

    Usage:
        printout("Hello world")                                   # logs to scriptname_log.log in current dir
        printout("Hello", "World", filename="custom_log.txt")     # logs to custom_log.txt in current dir
        printout("Hello", directory="logs")                       # logs to scriptname_log.log in 'logs' dir
        printout("Hello", filename="custom.txt", directory="logs")# logs to custom.txt in 'logs' dir
    """

    # Join message like regular print
    message = " ".join(str(arg) for arg in args)

    # Default log file name: script_name_log.log
    if filename is None:
        script_name = Path(sys.argv[0]).stem
        filename = f"{script_name}_log.log"

    # Use specified directory or current directory
    if directory is not None:
        log_dir = Path(directory)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / filename
    else:
        log_path = Path(filename)

    # Add timestamp to the log entry
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}\n"

    # Append to the log file
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Also print to stdout like normal print
    print(*args, **kwargs)