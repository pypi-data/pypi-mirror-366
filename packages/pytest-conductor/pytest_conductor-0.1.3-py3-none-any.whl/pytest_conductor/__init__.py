"""Pytest plugin for coordinating the order in which marked tests run."""

VERSION = "0.1.3"

# Import hooks to register them with pytest
from . import hooks  # noqa
