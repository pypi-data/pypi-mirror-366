"""Assonant ExternalLink class."""
from .data_handler import DataHandler


class ExternalLink(DataHandler):
    """Data class to handle a link that references a specific data from an external file."""

    name: str
    target_path: str
    filepath: str
