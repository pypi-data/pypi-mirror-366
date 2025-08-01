"""Assonant data parsers for data loggers.

This submodule defines Data Parsers objects to be used on Data Logger in order to interpretate
different types of data mapping/configuration files.
"""

from .assonant_data_retriever import AssonantDataRetriever

__all__ = [
    "AssonantDataRetriever",
]
