"""Log Manager -- with dual support for .py & jupyter notebook"""
# -*- coding: utf-8 -*-

import os
import sys
import ast
from datetime import datetime
from IPython.core.getipython import get_ipython
from IPython.core.magic import Magics, magics_class, cell_magic


class Logger:
    """
    DualLogger(log_path, timestamp=True, mode='a')\n
    Logs output to both console and a file simultaneously.

    Parameters:
        log_path (str): Path to the log file.
        timestamp (bool): If True, prefixes each line with timestamp. Default: True.
        mode (str): File write mode - 'a' (append) or 'w' (overwrite). Default: 'a'.

    --------------------
    🔹 Usage Examples 🔹
    --------------------

    In .py Scripts:
    ----------------
    ```python
    from logger import Logger

    logger = Logger("/home/user/logs/myscript.log", timestamp=True, mode='a')
    print("This will be logged with INFO level.")
    logger.log("Something went wrong", level="ERROR")
    logger.close()
    ```

    In Jupyter Notebook:
    ---------------------
    1. Load the extension:
    ```python
    %load_ext logger
    ```

    2. Use the cell magic to log:
    ```python
    %%log_to /home/user/logs/exp_log.txt
    %%log_to path=/path/to/log.txt timestamp=False mode=w
    print("This will be logged to both console and file.")
    ```
    """
    def __init__(self, filepath, timestamp=True, mode='a'):
        self.timestamp = timestamp
        self.terminal_out = sys.stdout
        self.terminal_err = sys.stderr

        # Ensure parent directory exists
        log_dir = os.path.dirname(os.path.abspath(filepath))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        if filepath:
            self.log_file = open(filepath, mode, buffering=1, encoding='utf-8')  # Line-buffered
            self._stdout_buffer = ""
            self._stderr_buffer = ""
            sys.stdout = self
            sys.stderr = self

    def _write_line(self, line, level="INFO"):
        ts = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " if self.timestamp else ""
        formatted_line = f"{ts}[{level.upper()}] {line}"
        self.terminal_out.write(line + "\n")
        self.log_file.write(formatted_line + "\n")
        self.flush()

    def write(self, message):
        """Route to stdout or stderr depending on the calling context"""
        caller_is_sys = sys._getframe(1).f_globals.get("__name__") == "sys"
        if caller_is_sys:
            self._stderr_buffer += message
            while "\n" in self._stderr_buffer:
                line, self._stderr_buffer = self._stderr_buffer.split("\n", 1)
                self._write_line(line, level="ERROR")
        else:
            self._stdout_buffer += message
            while "\n" in self._stdout_buffer:
                line, self._stdout_buffer = self._stdout_buffer.split("\n", 1)
                self._write_line(line, level="INFO")

    def log(self, message, level="INFO"):
        """Explicit log call with level."""
        self._write_line(message, level)

    def flush(self):
        self.terminal_out.flush()
        self.log_file.flush()

    def close(self):
        if self._stdout_buffer.strip():
            self._write_line(self._stdout_buffer.strip(), level="INFO")
        if self._stderr_buffer.strip():
            self._write_line(self._stderr_buffer.strip(), level="ERROR")
        self.flush()
        sys.stdout = self.terminal_out
        sys.stderr = self.terminal_err
        self.log_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


# ---------------------------
# Jupyter cell magic support
# ---------------------------
@magics_class
class LoggerMagics(Magics):
    @cell_magic
    def log_to(self, line, cell):
        """
        Log both to console and file.

        Usage:
        ```python
            %%log_to /path/to/log.txt
            %%log_to path=/path/to/log.txt timestamp=False mode=w
        ```
        """
        opts = {'mode': 'a', 'timestamp': True}
        for token in line.strip().split():
            if '=' in token:
                k, v = token.split('=', 1)
                opts[k] = ast.literal_eval(v) if k == 'timestamp' else v
            elif 'path' not in opts:
                opts['path'] = token

        if 'path' not in opts:
            raise ValueError("Must provide log path as `path=...` or a positional argument.")

        logger = Logger(opts['path'], opts['timestamp'], opts['mode'])
        try:
            # 👇 Use Jupyter's actual user namespace, not local `globals()`
            exec(cell, get_ipython().user_global_ns)
        finally:
            logger.close()


def load_ipython_extension(ipython):
    ipython.register_magics(LoggerMagics)
