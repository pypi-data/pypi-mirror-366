"""Tests focused on validating Assonant Components/Entry methods that add information to it"""

import pytest

from assonant.data_classes.data_handlers import Axis, DataField
from assonant.data_classes.enums import TransformationType
from assonant.data_classes.factories import AssonantDataHandlerFactory

from ..utils import (
    assert_axis_content,
    assert_axis_equality,
    assert_component_equality,
    assert_data_field_content,
    assert_data_fields_equality,
    get_fixture_values,
)
from .test_data_handler_factory import create_test_params_combinations


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(Axis))
def test_add_position(value, unit, metadata, transformation_type, example_base_component, request):
    """
    Validate that add_position method from Components correctly
    add Axis object to its internal positions dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must add Axis within its position dictionary
        - Added Axis must be identified with the same name it was given during add_position method
        - Axis object within Component positions dictionary must be equivalent to how it was before insertion
    """

    # To avoid creating lots of different fixtures, manually create Axis DataHandler using Factory
    # if this test passes, other tests related to adding Axis, don't need to deal with all data types.
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    axis = AssonantDataHandlerFactory.create_axis(
        transformation_type=transformation_type,
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )

    axis_name = "x"
    example_base_component.add_position(axis_name, axis.model_copy())

    # Assert Axis was add to positions dict
    assert len(example_base_component.positions.items()) == 1

    # Assert correct name was given to Axis within positions dict and that it remained unchanged.
    assert_axis_equality(example_base_component.positions[axis_name], axis)


def test_add_position_with_name_conflict(example_base_component, example_translation_axis, example_rotation_axis):
    """
    Validate that add_position method from Components correctly add Axis object to its internal
    positions dictionary and handles name conflicts.

    Expected Behavior:
        - Both added Axis must be within Component positions internal dict
        - The first added Axis must not suffer any change from how it was before
        - Any subsequent Axis added that has the same name with another already existing Axis from the poisitions
        dict from Component must have its name automatically updated to a new unique name by adding an index in
        front the original passed name (e.g: <axis_name> (1))
    """
    axis_name = "x"
    example_base_component.add_position(axis_name, example_translation_axis.model_copy())
    example_base_component.add_position(axis_name, example_rotation_axis.model_copy())

    # Assert both Axis objects were add to positions dict
    assert len(example_base_component.positions.items()) == 2

    # 1st Axis name and content must be unchanged
    assert_axis_equality(example_base_component.positions[axis_name], example_translation_axis)

    # 2nd Axis name must be the same as the 1st with an index due to name conflict and its content must be unchanged
    assert_axis_equality(example_base_component.positions[axis_name + " (1)"], example_rotation_axis)


@pytest.mark.parametrize("transformation_type", [t_type for t_type in TransformationType])
@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_create_and_add_position(value, unit, metadata, transformation_type, example_base_component, request):
    """
    Validate that create_and_add_position method from Components correctly
    create and add Axis object to its internal positions dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must create a new Axis with passed data
        - Base Component must add the new created Axis within its positions dictionary
        - Added Axis must be identified with the same name it was given during create_and_add_position method
        - Axis object created by the Component must preserve passed data values.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)
    input_transformation_type = transformation_type

    axis_name = "x"
    example_base_component.create_and_add_position(
        axis_name, input_transformation_type, input_value, input_unit, input_metadata
    )

    # Assert created Axis was add to positions dict
    assert len(example_base_component.positions.items()) == 1

    # Assert correct name was given to Axis within positions dict and that it remained unchanged
    assert_axis_content(
        example_base_component.positions[axis_name], input_value, input_unit, input_metadata, input_transformation_type
    )


def test_create_and_add_position_with_name_conflict(
    example_float_1d_array, example_int_1d_array, example_unit, example_metadata, example_base_component
):
    """
    Validate that create_and_add_position method from Components correctly
    create and add Axis object to its internal positions dictionary and handles name conflict.

    Expected Behavior:
        - Both Axis DataHandlers must be created
        - Both created Axis must be add to Component positions dictionary
        - The first create and added Axis must have its name and content preserved
        - The second create and added Axis must have its content preserved but name updated
        to a new unique name by adding an index in front of the original anem (e.g: <axis_name> (1))
    """
    axis_name = "x"
    example_base_component.create_and_add_position(
        axis_name, TransformationType.TRANSLATION, example_float_1d_array, example_unit, example_metadata
    )
    example_base_component.create_and_add_position(
        axis_name, TransformationType.ROTATION, example_int_1d_array, example_unit, example_metadata
    )

    # Assert both created Axis were add to positions dict
    assert len(example_base_component.positions.items()) == 2

    # 1st Axis name and content must be unchanged
    assert_axis_content(
        example_base_component.positions[axis_name],
        example_float_1d_array,
        example_unit,
        example_metadata,
        TransformationType.TRANSLATION,
    )

    # 2nd Axis name must be the same as the 1st with an index due to name conflict and its content must be unchanged
    assert_axis_content(
        example_base_component.positions[axis_name + " (1)"],
        example_int_1d_array,
        example_unit,
        example_metadata,
        TransformationType.ROTATION,
    )


def test_add_subcomponent(example_base_component, example_subcomponent):
    """
    Validate that add_subcomponent method from Components correctly
    add subcomponents to its internal dictionary.

    Expected Behavior:
        - Both added subcomponents must be within base_component internal sub_components dict
        - Added sub_components must be exactly equal to how it was before being add
    """
    example_subcomponent_2 = example_subcomponent.model_copy()
    example_subcomponent_2.name = "new unique name"

    # Add copies to avoid that internal manipulation changes external data and causing possible False-Positive result.
    example_base_component.add_subcomponent(example_subcomponent.model_copy())
    example_base_component.add_subcomponent(example_subcomponent_2.model_copy())

    assert len(example_base_component.subcomponents.items()) == 2
    assert_component_equality(example_base_component.subcomponents[example_subcomponent.name], example_subcomponent)
    assert_component_equality(example_base_component.subcomponents[example_subcomponent_2.name], example_subcomponent_2)


def test_add_subcomponent_with_name_conflict(example_base_component, example_subcomponent):
    """
    Validate that add_subcomponent method from Components correctly
    handle cases where subcomponent with conflicting name are add.

    Expected Behavior:
        - Both added subcomponents must be within base_component internal sub_components dict
        - The first added sub_components must not suffer any change from how it was before
        - Any subsequent sub_component added that has the same name with another already existing subcomponent
        must have its name automatically updated to a new unique name by adding an index in front the original
        name (e.g: sub_component (1))
    """
    example_subcomponent_2 = example_subcomponent.model_copy()

    example_base_component.add_subcomponent(example_subcomponent.model_copy())
    example_base_component.add_subcomponent(example_subcomponent_2.model_copy())

    assert len(example_base_component.subcomponents.items()) == 2

    # Assert that 1st subcomponent was totally unchanged
    assert_component_equality(example_base_component.subcomponents[example_subcomponent.name], example_subcomponent)

    with pytest.raises(AssertionError):
        # It is expected the assertion to fail, as subcomponent name should have been renamed,
        # otherwise name conflict handling failed
        assert_component_equality(
            example_base_component.subcomponents[example_subcomponent_2.name + " (1)"], example_subcomponent_2
        )

    # Assert it was only Component names that were different and caused previous AssertionError
    renamed_example_subcomponent_2 = example_subcomponent_2.model_copy()
    renamed_example_subcomponent_2.name = example_base_component.subcomponents[
        example_subcomponent_2.name + " (1)"
    ].name
    assert_component_equality(
        example_base_component.subcomponents[example_subcomponent_2.name + " (1)"], renamed_example_subcomponent_2
    )


def test_add_list_of_subcomponents(example_base_component, example_subcomponent):
    """
    Validate that add_subcomponent method from Components correctly
    add list of subcomponents to its internal dictionary.

    Expected Behavior:
        - All added subcomponents must be within base_component internal sub_components dict
        - Added sub_components must be exactly equal to how it was before being add
    """
    example_subcomponent_2 = example_subcomponent.model_copy()
    example_subcomponent_3 = example_subcomponent.model_copy()
    example_subcomponent_2.name = "2nd subcomponent"
    example_subcomponent_3.name = "3rd subcomponent"

    list_of_subcomponents = [
        example_subcomponent.model_copy(),
        example_subcomponent_2.model_copy(),
        example_subcomponent_3.model_copy(),
    ]

    # Add copies to avoid that internal manipulation changes external data and causing possible False-Positive result.
    example_base_component.add_subcomponent(list_of_subcomponents)

    assert len(example_base_component.subcomponents.items()) == len(list_of_subcomponents)
    assert_component_equality(example_base_component.subcomponents[example_subcomponent.name], example_subcomponent)
    assert_component_equality(example_base_component.subcomponents[example_subcomponent_2.name], example_subcomponent_2)
    assert_component_equality(example_base_component.subcomponents[example_subcomponent_3.name], example_subcomponent_3)


def test_add_list_of_subcomponents_with_name_conflict(example_base_component, example_subcomponent):
    """
    Validate that add_subcomponent method from Components correctly handle cases where subcomponent
    with conflicting name exists inside subcomponents list being.

    Expected Behavior:
        - All added subcomponents must be within base_component internal sub_components dict
        - The first added sub_components must not suffer any change from how it was before
        - Any subsequent sub_component added that has the same name with another already existing subcomponent
        must have its name automatically updated to a new unique name by adding an index in front the original
        name (e.g: sub_component (1))
    """
    example_subcomponent_2 = example_subcomponent.model_copy()
    example_subcomponent_3 = example_subcomponent.model_copy()

    list_of_subcomponents = [
        example_subcomponent.model_copy(),
        example_subcomponent_2.model_copy(),
        example_subcomponent_3.model_copy(),
    ]

    # Add copies to avoid that internal manipulation changes external data and causing possible False-Positive result.
    example_base_component.add_subcomponent(list_of_subcomponents)

    assert len(example_base_component.subcomponents.items()) == len(list_of_subcomponents)

    # Assert that 1st subcomponent was totally unchanged
    assert_component_equality(example_base_component.subcomponents[example_subcomponent.name], example_subcomponent)

    with pytest.raises(AssertionError):
        # It is expected the assertion to fail, as subcomponent name should have been renamed,
        # otherwise name conflict handling failed
        assert_component_equality(
            example_base_component.subcomponents[example_subcomponent_2.name + " (1)"], example_subcomponent_2
        )

    # Assert it was only Component names that were different and caused previous AssertionError
    renamed_example_subcomponent_2 = example_subcomponent_2.model_copy()
    renamed_example_subcomponent_2.name = example_base_component.subcomponents[
        example_subcomponent_2.name + " (1)"
    ].name
    assert_component_equality(
        example_base_component.subcomponents[example_subcomponent_2.name + " (1)"], renamed_example_subcomponent_2
    )

    with pytest.raises(AssertionError):
        # It is expected the assertion to fail, as subcomponent name should have been renamed,
        # otherwise name conflict handling failed
        assert_component_equality(
            example_base_component.subcomponents[example_subcomponent_3.name + " (2)"], example_subcomponent_3
        )

    # Assert it was only Component names that were different and caused previous AssertionError
    renamed_example_subcomponent_3 = example_subcomponent_3.model_copy()
    renamed_example_subcomponent_3.name = example_base_component.subcomponents[
        example_subcomponent_3.name + " (2)"
    ].name
    assert_component_equality(
        example_base_component.subcomponents[example_subcomponent_3.name + " (2)"], renamed_example_subcomponent_3
    )


@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_add_field(value, unit, metadata, example_base_component, request):
    """
    Validate that add_field method from Components correctly
    add DataField object to its internal fields dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must add DataField within its fields dictionary
        - Added DataField must be identified with the same name it was given during add_field method
        - DataField object within Component fields dictionary must be equivalent to how it was before insertion
    """

    # To avoid creating lots of different fixtures, manually create DataField DataHandler using Factory
    # if this test passes, other tests related to adding DataField, don't need to deal with all data types.
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    data_field = AssonantDataHandlerFactory.create_data_field(
        value=input_value,
        unit=input_unit,
        extra_metadata=input_metadata,
    )

    data_field_name = "data_field"
    example_base_component.add_field(data_field_name, data_field.model_copy())

    # Assert DataField was add to fields dict
    assert len(example_base_component.fields.items()) == 1

    # Assert correct name was given to DataField within fields dict and that it remained unchanged.
    assert_data_fields_equality(example_base_component.fields[data_field_name], data_field)


def test_add_field_with_name_conflict(
    example_base_component, example_int_1d_array_data_field, example_float_2d_array_data_field
):
    """
    Validate that add_field method from Components correctly add DataField object to its internal
    fields dictionary and handles name conflicts.

    Expected Behavior:
        - Both added DataFields must be within Component fields internal dict
        - The first added DataField must not suffer any change from how it was before
        - Any subsequent DataField added that has the same name with another already existing from the fields
        dict from Component must have its name automatically updated to a new unique name by adding an index in
        front the original passed name (e.g: <field_name> (1))
    """
    field_name = "field_name"
    example_base_component.add_field(field_name, example_int_1d_array_data_field.model_copy())
    example_base_component.add_field(field_name, example_float_2d_array_data_field.model_copy())

    # Assert both DataField objects were add to positions dict
    assert len(example_base_component.fields.items()) == 2

    # 1st DataField name and content must be unchanged
    assert_data_fields_equality(example_base_component.fields[field_name], example_int_1d_array_data_field)

    # 2nd DataField name must be the same as the 1st with a index due to name conflict and its content must be unchanged
    assert_data_fields_equality(example_base_component.fields[field_name + " (1)"], example_float_2d_array_data_field)


@pytest.mark.parametrize("value, unit, metadata", create_test_params_combinations(DataField))
def test_create_and_add_field(value, unit, metadata, example_base_component, request):
    """
    Validate that create_and_add_field method from Components correctly
    create and add DataField object to its internal fields dictionary for all accepted data types.

    Expected Behavior:
        - Base Component must create a new DataField with passed data
        - Base Component must add the new created DataField within its fields dictionary
        - Added DataField must be identified with the same name it was given during create_and_add_field method
        - DataField object created by the Component must preserve passed data values.
    """
    input_value = get_fixture_values(value, request)
    input_unit = get_fixture_values(unit, request)
    input_metadata = get_fixture_values(metadata, request)

    data_field_name = "data_field"
    example_base_component.create_and_add_field(data_field_name, input_value, input_unit, input_metadata)

    # Assert created DataField was add to fields dict
    assert len(example_base_component.fields.items()) == 1

    # Assert correct name was given to DataField within fields dict and that it remained unchanged
    assert_data_field_content(example_base_component.fields[data_field_name], input_value, input_unit, input_metadata)


def test_create_and_add_field_with_name_conflict(
    example_float_1d_array, example_int_1d_array, example_unit, example_metadata, example_base_component
):
    """
    Validate that create_and_add_field method from Components correctly
    create and add DataField object to its internal fields dictionary and handles name conflict.

    Expected Behavior:
        - Both DataFields must be created
        - Both created DataFields must be add to Component fields dictionary
        - The first create and added DataField must have its name and content preserved
        - The second create and added DataField must have its content preserved but name updated
        to a new unique name by adding an index in front of the original anem (e.g: <data_field_name> (1))
    """
    data_field_name = "data_field"
    example_base_component.create_and_add_field(data_field_name, example_float_1d_array, example_unit, example_metadata)
    example_base_component.create_and_add_field(data_field_name, example_int_1d_array, example_unit, example_metadata)

    # Assert both created DataFields were add to fields dict
    assert len(example_base_component.fields.items()) == 2

    # 1st DataField name and content must be unchanged
    assert_data_field_content(
        example_base_component.fields[data_field_name], example_float_1d_array, example_unit, example_metadata
    )

    # 2nd DataField name must be the same as the 1st with an index due to name conflict and
    # its content must be unchanged
    assert_data_field_content(
        example_base_component.fields[data_field_name + " (1)"], example_int_1d_array, example_unit, example_metadata
    )


# To test Axis failure and Data Field failure during insertion, pass wrong class to name param
# Test add subcomponent failure - exception raising
# Test add position failure - exception raising
# Test add field failure - exception raising
# Test create_and_add_position failure - exception raising
# Test create_and_add_field failure - exception raising


# Test create_and_add_timeseries_position failure - exception raising
# Test create_and_add_timeseries_position all valid data type combinations accepted
# Test create_and_add_timeseries_position duplicated
# Test create_and_add_field duplicated
# Test create_and_add_timeseries_field failure - exception raising
# Test create_and_add_timeseries_field for all valid data type combinations accepted
# Test create_and_add_timeseries_field duplicated
# Test create_data_handler generic method for all valid types accepted
# Test create_data_handler generic method duplicated for all types of data_handlers
# Test create_data_handler generic failed - exception raising
# Test take_data_handlers_from method
# Test generate_new_valid_name method
# Test indexed_name_generator method
# Test Components Constructors for all type of Components
