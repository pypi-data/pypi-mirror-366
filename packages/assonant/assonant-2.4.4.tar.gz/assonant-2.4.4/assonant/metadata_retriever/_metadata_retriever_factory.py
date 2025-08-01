from pathlib import Path

from ._assonant_metadata_retriever_interface import IAssonantMetadataRetriever
from ._csv_metadata_retriever import CSVMetadataRetriever
from .enums import MetadataSourceFileFormat
from .exceptions import AssonantMetadataRetrieverError


class MetadataRetrieverFactory:
    """Metadata Retriever Factory.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Metadata Retrievers.
    """

    def create_metadata_retriever(self, metadata_source_file_path: str) -> IAssonantMetadataRetriever:
        """Public method that abstracts metadata retriever creation process for the factory user.

        Internally, this method deals with validation and specific Metadata Retriever
        creation

        Args:
            metadata_source_file_path (str): Path to metadata source file.

        Raises:
            AssonantMetadataRetrieverError: An error occured during the creation of
            the respective Metadata Retriever.

        Returns:
            IAssonantMetadataRetriever: Data Retriever instance which implements the
            IAssonantMetadataRetriever interface for the given data_source_file_format.
        """
        file_format = self._get_file_format(metadata_source_file_path)

        self._validate_file_format(file_format)

        if file_format == MetadataSourceFileFormat.CSV.value:
            return self._create_csv_metadata_retriever(metadata_source_file_path)

        raise AssonantMetadataRetrieverError(
            f"'{file_format}' file format is set as supported but its creation method is not implemented."
        )

    def _create_csv_metadata_retriever(self, metadata_source_file_path: str) -> CSVMetadataRetriever:
        """Create CSVMetadataRetriver

        Args:
            metadata_source_file_path (str): Path to metadata source file

        Returns:
            CSVDataRetriever: Instance of CSVMetadataRetriever to deal data from passed data_source_file_path.
        """
        return CSVMetadataRetriever(csv_file_path=metadata_source_file_path)

    def _validate_file_format(self, file_format: str):
        """Check if file format is supported

        Args:
            file_format (str): Data source file format extension.

        Raises:
            AssonantDataRetrieverError: File format is not supported
        """

        if file_format not in MetadataSourceFileFormat._value2member_map_:
            raise AssonantMetadataRetrieverError(f"'{file_format}' is not supported by Metadata Retriever!")

    def _get_file_format(self, data_source_file_path: str) -> str:
        """Get file extension from given path

        Args:
            data_source_file_path (str): Path to data source file.

        Raises:
            AssonantDataRetrieverError: Erro raised if path passed is not from a file.

        Returns:
            str: File extesion without '.' character.
        """

        with Path(data_source_file_path) as path:
            if path.is_file():
                # Get file extension and remove the '.' character
                return path.suffix[1:]
            else:
                raise AssonantMetadataRetrieverError(f"'{data_source_file_path}' is not a file!")
