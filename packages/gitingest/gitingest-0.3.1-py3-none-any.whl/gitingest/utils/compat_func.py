"""Compatibility functions for Python 3.8."""

import os
from pathlib import Path


def readlink(path: Path) -> Path:
    """Read the target of a symlink.

    Compatible with Python 3.8.

    Parameters
    ----------
    path : Path
        Path to the symlink.

    Returns
    -------
    Path
        The target of the symlink.

    """
    return Path(os.readlink(path))


def removesuffix(s: str, suffix: str) -> str:
    """Remove a suffix from a string.

    Compatible with Python 3.8.

    Parameters
    ----------
    s : str
        String to remove suffix from.
    suffix : str
        Suffix to remove.

    Returns
    -------
    str
        String with suffix removed.

    """
    return s[: -len(suffix)] if s.endswith(suffix) else s
