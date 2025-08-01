"""General use utilitary methods"""

from typing import Any, Iterable, List, Union

import numpy as np

from assonant.data_classes.components import Component
from assonant.data_classes.data_handlers import Axis, DataField, TimeSeries
from assonant.data_classes.enums import TransformationType


def array_equal_safe_against_none_and_nan(
    a1: Union[List, np.typing.NDArray], a2: Union[List, np.typing.NDArray]
) -> bool:
    """Compare two arrays/lists if they are element-wise equal in a safe way against None and np.nan values.

    This method was create due to np.array_equals breaking if None value is passed when its equal_nan
    flag is set to True as np.isnan() methos used internally doesn't support None as input.

    Args:
        a1 (Union[List, np.typing.NDArray]): Array or List to be compared against a2.
        a2 (Union[List, np.typing.NDArray]): Array or List to be compared against a1.

    Returns:
        bool: True if a1 equals to a2 and False if not.
    """
    if a1 is Iterable and a2 is Iterable:
        if len(a1) != len(a2):
            # Different lengths, they are directly different.
            return False

    if np.array_equal(a1, a2):
        # Just a normal case of two equal arrays/lists.
        return True
    else:
        # Failure may be due to np.nan != np.nan so a specific comparsion need to be done
        # However, numpy method that does that breaks if None pass is passed. Due to that, an
        # element-wise comparison must be done and checking directly how to deal with specific cases.
        for v1, v2 in zip(a1, a2):
            if type(v1) is not type(v2):
                # Cover comparison between None and np.nan. ALso guarantee this will not happen
                # on underlying comparisons
                return False
            elif v1 is not None and v2 is not None:
                # Cover comparison using np.nan.
                if not np.array_equal(v1, v2, equal_nan=True):
                    return False
            else:
                # Cover comparison using None.
                if not np.array_equal(v1, v2):
                    return False

        # All elements were verified and no difference found, that means a1 == a2.
        return True


def compare_dicts(d1, d2):
    """Recursively compare two dictionaries, handling numpy arrays."""

    if d1 is not None and d2 is not None:
        if d1.keys() != d2.keys():
            # If dict keys are different, they are clearly different
            return False

        for key in d1:
            # Check equality of each dict element
            v1 = d1[key]
            v2 = d2[key]

            if isinstance(v1, dict) and isinstance(v2, dict):
                if not compare_dicts(v1, v2):
                    return False
            elif not array_equal_safe_against_none_and_nan(v1, v2):
                return False

    return True


def get_fixture_values(fixture: Union[str, None], request) -> Union[Any, None]:
    """Wrapper class to handle getting fixture values based in their names.

    Args:
        fixture (Union[str, None]): Fixture name or None value.
        request (pytest.FixtureRequest): request fixture object from pytest.

    Returns:
       Union[Any, None]: Retrieved fixture value if not None else returns None.
    """

    fixture_value = request.getfixturevalue(fixture) if fixture is not None else None

    return fixture_value


def assert_data_field_content(data_field: DataField, input_value: Any, input_unit: Any, input_metadata: Any):
    """Assert that DataField was correctly created based on input values.

    Args:
        data_field (DataField): DataField which assertion will be applied over.
        input_value (Any): Input value parameter during DataField creation.
        input_unit (Any): Input unit parameter during DataField creation.
        input_metadata (Any): Input metadata parameter during DataField creation.

    Raise:
        AssertionError: Raises if any assertion fails.
    """
    assert isinstance(data_field, DataField)
    assert array_equal_safe_against_none_and_nan(data_field.value, input_value)
    assert data_field.unit == input_unit
    assert compare_dicts(data_field.extra_metadata, input_metadata)


def assert_timeseries_content(
    timeseries: TimeSeries,
    input_value: Any,
    input_unit: Any,
    input_metadata: Any,
    input_timestamps: Any,
    input_timestamps_unit: Any,
    input_timestamps_metadata: Any,
):
    """Assert that TimeSeries was correctly created based on input values.

    Args:
        timeseries (TimeSeries): TimeSeries which assertion will be applied over.
        input_value (Any): Input value parameter during TimeSeries creation.
        input_unit (Any): Input unit parameter during TimeSeries creation.
        input_metadata (Any): Input metadata parameter during TimeSeries creation.
        input_timestamps (Any): Input timestamps parameter during TimeSeries creation.
        input_timestamps_unit (Any): Input timestamps unit parameter during TimeSeries creation.
        input_timestamps_metadata (Any): Input timestamps metadata parameter during TimeSeries creation.

    Raise:
        AssertionError: Raises if any assertion fails.
    """
    assert isinstance(timeseries, TimeSeries)
    assert_data_field_content(timeseries.value, input_value, input_unit, input_metadata)
    assert_data_field_content(timeseries.timestamps, input_timestamps, input_timestamps_unit, input_timestamps_metadata)


def assert_axis_content(
    axis: Axis,
    input_value: Any,
    input_unit: Any,
    input_metadata: Any,
    input_transformation_type: TransformationType,
    input_timestamps: Any = None,
    input_timestamps_unit: Any = None,
    input_timestamps_metadata: Any = None,
):
    """Assert that Axis was correctly created based on input values.

    Args:
        axis (Axis): Axis which assertion will be applied over.
        input_value (Any): Input value parameter during Axis creation.
        input_unit (Any): Input unit parameter during Axis creation.
        input_metadata (Any): Input metadata parameter during Axis creation.
        input_transformation_type(TransformationType): Input transformation type parameter during Axis creation.
        input_timestamps (Optional, Any): Input timestamps param during Axis creation. Defaults to None.
        input_timestamps_unit (Optional, Any): Input timestamps unit param during Axis creation. Defaults to None.
        input_timestamps_metadata (Optional, Any): Input timestamps metadata param on Axis creation. Defaults to None.

    Raise:
        AssertionError: Raises if any assertion fails.
    """
    assert isinstance(axis, Axis)
    assert axis.transformation_type == input_transformation_type
    if type(axis.value) is DataField:
        assert_data_field_content(axis.value, input_value, input_unit, input_metadata)
    elif type(axis.value) is TimeSeries:
        assert_timeseries_content(
            axis.value,
            input_value,
            input_unit,
            input_metadata,
            input_timestamps,
            input_timestamps_unit,
            input_timestamps_metadata,
        )
    else:
        raise AssertionError(f"{type(axis.value)} is a invalid type for Axis value property!")


def assert_data_fields_equality(df1: DataField, df2: DataField):
    """Assert two Assonant DataField are equal by comparing their content.

    Args:
        df1 (DataField): DataField which content will be compared to df2.
        df2 (DataField): DataField which content will be compared to df1.
    """
    assert_data_field_content(df1, df2.value, df2.unit, df2.extra_metadata)


def assert_timeseries_equality(ts1: TimeSeries, ts2: TimeSeries):
    """Assert two Assonant TimeSeries are equal by comparing their content.

    Args:
        ts1 (TimeSeries): TimeSeries which content will be compared to ts2.
        ts2 (TimeSeries): TimeSeries which content will be compared to ts1.
    """
    assert_timeseries_content(
        ts1,
        ts2.value.value,
        ts2.value.unit,
        ts2.value.extra_metadata,
        ts2.timestamps.value,
        ts2.value.unit,
        ts2.value.extra_metadata,
    )


def assert_axis_equality(ax1: Axis, ax2: Axis):
    """Assert two Assonant Axis are equal by comparing their content.

    Args:
        ax1 (Axis): Axis which content will be compared to ax2.
        ax2 (Axis): Axis which content will be compared to ax1.
    """

    # If Axis internal DataHandler is not from the same type, the assertion automatically fails
    assert type(ax1.value) is type(ax2.value)

    if type(ax1.value) is DataField:
        assert_axis_content(ax1, ax2.value.value, ax2.value.unit, ax2.value.extra_metadata, ax2.transformation_type)
    elif type(ax1.value) is TimeSeries:
        assert_axis_content(
            ax1,
            ax2.value.value.value,
            ax2.value.value.unit,
            ax2.value.value.extra_metadata,
            ax2.transformation_type,
            ax2.value.timestamps.value,
            ax2.value.timestamps.unit,
            ax2.value.timestamps.extra_metadata,
        )


def assert_component_equality(c1: Component, c2: Component):
    """Assert two Assonant Components are equal by comparing recursively their content dicts.

    Args:
        c1 (Component): Component which content will be compared to c2.
        c2 (Component): Component which content will be compared to c1.
    """

    # If both Components subcomponents keys are not equal, they are clearly different
    assert c1.subcomponents.keys() == c2.subcomponents.keys()

    # Check if Components fields and positions are equal
    assert c1.name == c2.name
    assert compare_dicts(c1.fields, c2.fields)
    assert compare_dicts(c1.positions, c2.positions)

    # Make a Recursive DFS to verify equality of all subcomponents
    for key in c1.subcomponents.keys():
        assert_component_equality(c1.subcomponents[key], c2.subcomponents[key])
