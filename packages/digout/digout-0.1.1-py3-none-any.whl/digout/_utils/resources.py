"""A module to manage resources and utilities for digout."""

from __future__ import annotations

import atexit
from contextlib import ExitStack
from functools import lru_cache
from importlib.resources import as_file, files
from pathlib import Path
from tempfile import TemporaryDirectory

# Create an exit stack to close resources properly on exit of the program,
# without having to use a context manager every time.
# (not so clean but I don't want to change the existing code structure)
# If digout is not used as a library, this doesn't even matter
# because the resources are not temporarily copied.
_exit_stack = ExitStack()
atexit.register(_exit_stack.close)


@lru_cache(maxsize=1)
def get_lbenv_script() -> Path:
    """Get the script that sources the LbEnv environment.

    The bash script is located at `digout/script/_source_lbenv.sh`.
    It is loaded as a resource from the `digout.script` package.
    """
    return _exit_stack.enter_context(
        as_file(files("digout.script") / "_source_lbenv.sh")
    )


def get_tmpdir() -> Path:
    """Get a temporary directory.

    This directory is created with a prefix of "digout_tmp_",
    and is cleaned up when the program exits.
    The temporary directory IS NOT CACHED so that it provides a fresh directory
    every time it is called.
    """
    return Path(
        _exit_stack.enter_context(TemporaryDirectory(prefix="digout_tmp_"))
    ).resolve()
