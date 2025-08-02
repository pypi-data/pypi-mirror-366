"""Assonant class to handle writing data from AssonantDataClasses into files."""

import os
from typing import Generator, List

from assonant.data_classes import AssonantDataClass

from ._assonant_file_writer_interface import IAssonantFileWriter
from ._file_writer_factory import FileWriterFactory
from .exceptions import FileAlreadyExistsError


class AssonantFileWriter(IAssonantFileWriter):
    """Assonant File Writer. Wrapper class to deal with writing data from AssonantDataClass into files.

    Wrapper class that abstracts all process related to creating specific file writers,
    writing data on files following the requirements of the given format.
    """

    _factory = FileWriterFactory()

    def __init__(self, file_format: str):
        # Persist file format
        self.file_format = file_format

        # Create specific file writer based on chosen file format
        self.file_writer = self._factory.create_file_writer(file_format)
        self.file_extension = self.file_writer.get_file_extension()

    def write_data(self, filepath: str, filename: str, data: AssonantDataClass):
        """Method for writing data using the specific FileWriter respective to define file format.

        If fail to save on target filepath, in order to avoid losing acquired data, it will try
        to save locally in current working directory.

        Args:
            filepath (str): Path where file will be saved.
            filename (str): Name that will be given to file.
            data (AssonantDataClass): AssonantDataClass that contains data to be saved in file.
        """
        try:
            # Create target directory if it does not exist
            os.makedirs(filepath, exist_ok=True)

            indexed_filename_generator = self._indexed_name_generator(filename)
            indexed_filename = filename

            while True:
                try:
                    self.file_writer.write_data(filepath, indexed_filename, data)
                    break  # If no exception was raised, data was sucessfully written.
                except FileAlreadyExistsError:
                    # In case the file already exists, test next indexed_filename and try writing data again
                    indexed_filename = next(indexed_filename_generator)
                    continue
                except Exception as e:
                    # Any other kind of Exception signalizes a critical failure!
                    raise e
        except Exception as e:
            # Treat Critical Failure
            workdir_filepath = os.path.join(os.getcwd())
            print(
                f"Failed to save data at {filepath} due the following exception: {repr(e)}. Trying to save file in current workdir..."
            )
            try:
                unique_filename = self._create_unique_filename(
                    workdir_filepath, filename
                )  # Create unique filename to avoid conflict failure.
                self.file_writer.write_data(workdir_filepath, unique_filename, data)
                print(f"File saved at current work directory (path: {workdir_filepath})")
            except Exception as e:
                print("Failed to save data locally in current work directory. Data lost.")
                raise e

    def get_file_extension(self) -> str:
        """Getter method for the file extension of currently handled file writer.

        Returns:
            str: File extenstion of urrently handled file writer.
        """
        return self.file_extension

    def get_supported_file_formats(self) -> List[str]:
        """Getter method for current supported file formats.

        Returns:
            List[str]: List containing curretly supported file formats.
        """
        return self._factory.get_supported_file_formats()

    def _create_unique_filename(self, filepath: str, filename: str) -> str:
        """Return a unique file name to be saved on target filepath.

        Args:
            filepath (str): Path where file will be saved
            filename (str): Current filename.

        Returns:
            str: Unique filename that can be saved on target filepath. If current filename
            is already unique, it will be returned as it is. Otherwise, a index will be
            concatenated to the filename
        """
        new_name_generator = self._indexed_name_generator(filename)
        filename = next(new_name_generator)
        complete_file_path = self._mount_complete_file_path(filepath, filename)
        while os.path.exists(complete_file_path):
            filename = next(new_name_generator)
            complete_file_path = self._mount_complete_file_path(filepath, filename)
        return filename

    def _mount_complete_file_path(self, filepath: str, filename: str) -> str:
        """Mount complete path to the file.

        Args:
            filepath (str): Path where file will be saved.
            filename (str): Name of the file.

        Returns:
            str: Complete path for the file: File path + file name + file extension
        """
        return os.path.join(filepath, os.path.splitext(filename)[0]) + self.file_extension

    def _indexed_name_generator(self, name: str) -> Generator[str, None, None]:
        """Generator for creating indexed names.

        Args:
            name (str): Reference name to be indexed by generator.

        Yields:
            Generator[str, None, None]: New indexed name based on passed name.
        """
        i = 1
        while True:
            new_name = f"{name}_{i:06d}"
            yield new_name
            i += 1
