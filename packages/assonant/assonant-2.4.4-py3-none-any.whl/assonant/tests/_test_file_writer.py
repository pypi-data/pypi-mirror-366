"""
from typing import Tuple

import pytest

from assonant.data_classes import Entry
from assonant.data_classes.data_handlers import Axis, DataField, DataHandler, TimeSeries
from assonant.data_classes.enums import TransformationType
from assonant.data_classes.factories import (
    AssonantComponentFactory,
    AssonantDataHandlerFactory,
    AssonantEntryFactory,
)
from assonant.file_writer import AssonantFileWriter
from assonant.naming_standards import BeamlineName


@pytest.fixture(scope="session")
def good_nexus_file_writer() -> AssonantFileWriter:
    return AssonantFileWriter(file_format='nexus')

@pytest.fixture(scope="session")
def int_data_field_complete() -> Tuple[str,DataField]:
    return (
        'complete_int_data_field',
        AssonantDataHandlerFactory.create_data_field(
            value=10,
            unit='mm',
            extra_metadata={
                'metadata_1': 'I am a field metadata',
                'metadata_2': 12.34
            }
        )
    )

def int_data_field_missing_unit() -> Tuple[str,DataField]:
    return (
        'complete_int_data_field',
        AssonantDataHandlerFactory.create_data_field(
            value=10,
            extra_metadata={
                'metadata_1': 'I am a field metadata',
                'metadata_2': 12.34
            }
        )
    )


@pytest.fixture(scope="session")
def example_entry() -> Entry:

    mirror = AssonantComponentFactory.create_component_by_class_name('Mirror','M1')
    print(mirror)
    mirror.create_and_add_position(
        name='rx',
        transformation_type=TransformationType.ROTATION,
        value='65',
        unit='degrees'
    )
    mirror.create_and_add_position(
        name='ry',
        transformation_type=TransformationType.ROTATION,
        value='30',
        unit='degrees'
    )

    entry = AssonantEntryFactory.create_entry('entry', BeamlineName.MANACA)
    print(entry)
    return entry.beamline.add_subcomponent([mirror])
    
@pytest.fixture(scope="function")
def base_tmp_dir_path(tmp_path_factory) -> str:
    return str(tmp_path_factory.mktemp('test'))


@pytest.fixture(scope="function")
def test_write_data_fields():




#def test_nexus_write(good_nexus_file_writer: AssonantFileWriter, base_tmp_dir_path: str, example_entry: Entry):
#
#    good_nexus_file_writer.write_data(
#        base_tmp_dir_path,
#        'test_filename',
#        example_entry
#    )
#
#    assert True==True




#def test_none_field_write():

#def test_none_name_field_write():

#def test_none_name_group_write():

#def test_subcomponent_write():

#def test_nexus_entries_write():

#def test_nexus_entry_conflict_handling():

#def test_local_writing_after_failure():

#def test_failure_due_to_wrong_filepath():

#def test_failure_due_to_invalid_format():
"""
