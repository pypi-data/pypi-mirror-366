# coding: utf-8

"""
Quantdle Python Client

A user-friendly Python client for downloading financial market data from Quantdle.
Features efficient direct HTTP requests instead of complex auto-generated swagger code.
"""

from __future__ import absolute_import

__version__ = "1.0.0"  # Updated version to match pyproject.toml

# Import main client (only thing users need)
from .client import Client

__all__ = [
    "Client",
]