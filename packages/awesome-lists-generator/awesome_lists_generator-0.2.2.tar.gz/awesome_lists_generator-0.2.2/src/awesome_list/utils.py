import re
import sys
import os





url_validator = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.IGNORECASE)
def is_url_valid(url: str) -> bool:
    return re.match(url_validator, url) is not None

def exit_process(code: int = 0) -> None:
    """Exit the process with exit code.

    `sys.exit` seems to be a bit unreliable, process just sleeps and does not exit.
    So we are using os._exit instead and doing some manual cleanup.
    """
    import atexit
    import gc

    gc.collect()
    atexit._run_exitfuncs()
    sys.stdout.flush()
    os._exit(code)