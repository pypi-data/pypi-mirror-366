from typing import List

from ._assonant_file_writer_interface import IAssonantFileWriter
from ._nexus_file_writer import NexusFileWriter
from .exceptions import AssonantFileWriterError


class FileWriterFactory:
    """File Writer Factory.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant File Writers
    """

    _supported_file_formats = ["nexus"]

    def create_file_writer(self, file_format: str) -> IAssonantFileWriter:
        """Public method that abstracts file writer creation process for the factory user.

        Internally, this method deals with validation and specific File Writer
        creation

        Args:
            file_format (str): Target file format that data will be written.

        Raises:
            AssonantFileWriterError: An error occured during the creation of
            the respective File Writer.

        Returns:
            IAssonantFileWriter: File Writer instance which implements the
            IAssonantFileWriter interface
        """
        self._validate_file_format(file_format)

        if file_format == "nexus":
            return self._create_nexus_file_writer()

        raise AssonantFileWriterError(
            f"'{file_format}' file format is set as supported but its creation method is not implemented."
        )

    def _create_nexus_file_writer(self) -> NexusFileWriter:
        return NexusFileWriter()

    def _validate_file_format(self, file_format: str) -> None:
        """Validate if passed file format is currently supported.

        Args:
            file_format (str): File format to be validated.

        Raises:
            AssonantFileWriterError: File format not supported.
        """
        if file_format not in self._supported_file_formats:
            raise AssonantFileWriterError(
                f"'{file_format}' file format isn't currently supported. "
                f"The supported file formats are: {self._supported_file_formats}"
            )

    def get_supported_file_formats(self) -> List[str]:
        """Getter method for private property 'supported_file_formats'.

        Returns:
            List[str]: List containing curretly supported file formats.
        """
        return self._supported_file_formats
