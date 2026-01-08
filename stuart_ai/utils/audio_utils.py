import os
import sys
import contextlib

@contextlib.contextmanager
def ignore_stderr():
    """Context manager to suppress stderr at the C level.
    Useful for silencing ALSA/Jack error messages from PyAudio.
    """
    # Only applicable on Unix-like systems
    if sys.platform == "win32":
        yield
        return

    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        sys.stderr.flush()
        os.dup2(devnull, 2)
        os.close(devnull)
        try:
            yield
        finally:
            os.dup2(old_stderr, 2)
            os.close(old_stderr)
    except Exception:
        # If anything goes wrong with the suppression, just yield
        yield
