import os
import sys
from datetime import datetime

def printout(*args, filename=None, **kwargs):
    """
    A print function that also logs output to a file.

    Usage:
        printout("Hello world")               # logs to scriptname_log.log
        printout("Hello", "World", filename="custom_log.txt")
    """

    # Join message like regular print
    message = " ".join(str(arg) for arg in args)

    # Default log file name: script_name_log.log
    if filename is None:
        script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        filename = f"{script_name}_log.log"

    # Add timestamp to the log entry
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}\n"

    # Append to the log file in current directory
    with open(filename, "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Also print to stdout like normal print
    print(*args, **kwargs)