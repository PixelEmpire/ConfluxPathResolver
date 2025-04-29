# utils.py

import os
import glob
import re
from typing import Optional


def expand_env_vars(path: str) -> str:
    """
        Expand $VAR or ${VAR} from environment variables in the path.
        Example: $HOME or ${HOME} will be replaced with the value of the HOME environment variable.

        :param path: The path to expand.
    """
    return os.path.expandvars(path)


def expand_wildcards(path: str) -> Optional[str]:
    """
        Expand wildcard patterns using glob and return the first match.
        If no match is found, return None.

        :param path: The path to expand.
        :return: The first matching path or None if no match is found.
    """
    matches = glob.glob(path)
    return matches[0] if matches else None


def pad_frame(frame: int, padding: int) -> str:
    """
        Return the frame number zero-padded to the given width.
        Example: pad_frame(5, 4) returns '0005'.

        :param frame: The frame number to pad.
        :param padding: The total width of the padded string.
    """
    return str(frame).zfill(padding)


def contains_wildcard(path: str) -> bool:
    """
        Check if the path contains wildcard characters.

        :param path: The path to check.
        :return: True if the path contains wildcard characters, False otherwise.
    """
    return "*" in path or "?" in path or "[" in path


def extract_tokens(template_str: str) -> list:
    """
        Extract all token names from a string like 'foo/{bar}/baz'.
        Returns a list of token names, e.g., ['bar'].

        :param template_str: The string containing tokens.
        :return: A list of token names.
    """
    return re.findall(r"\{([a-zA-Z0-9_.]+)\}", template_str)
