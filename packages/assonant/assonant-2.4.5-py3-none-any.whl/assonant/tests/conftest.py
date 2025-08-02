import random
from typing import Generator, List, Union

import numpy as np
import pytest

from assonant.data_classes.components import Component
from assonant.data_classes.enums import TransformationType
from assonant.data_classes.factories import (
    AssonantComponentFactory,
    AssonantDataHandlerFactory,
    AssonantEntryFactory,
)
from assonant.naming_standards import BeamlineName


@pytest.fixture(scope="session")
def fixed_seed_random_generator() -> Generator:
    """
    Provides a NumPy random number generator with a fixed seed (42) to ensure reproducibility across tests.
    """
    return np.random.default_rng(seed=42)


# ======= Non-array data =======


@pytest.fixture(scope="session")
def example_int_value() -> int:
    """
    Provides a sample integer value for basic test cases.
    """
    return 1234


@pytest.fixture(scope="session")
def example_float_value() -> float:
    """
    Provides a sample float value for basic test cases.
    """
    return 43.21


@pytest.fixture(scope="session")
def example_string_value() -> float:
    """
    Provides a sample string value for basic test cases.
    """
    return "example value"


# ======= 1D data as numpy arrays =======


@pytest.fixture(scope="session")
def example_int_1d_array(fixed_seed_random_generator) -> np.typing.NDArray:
    """
    Provides a 1D NumPy array of integers (length 10) with values from 0 to 255.
    """
    return fixed_seed_random_generator.integers(0, 256, 10)


@pytest.fixture(scope="session")
def example_float_1d_array(fixed_seed_random_generator) -> np.typing.NDArray:
    """
    Provides a 1D NumPy array of floats (length 10) with values in [0, 1).
    """
    return fixed_seed_random_generator.random(10)


@pytest.fixture(scope="session")
def example_string_1d_array() -> np.typing.NDArray:
    """
    Provides a 1D NumPy array of sample string values.
    """
    return np.array(["a", "b", "c", "d", "e"])


@pytest.fixture(scope="session")
def example_float_1d_array_with_nan(example_float_1d_array) -> np.typing.NDArray:
    """
    Provides a copy of a float 1D NumPy array with NaNs injected at the start, middle, and end.
    Useful for testing NaN-safe operations.
    """
    float_1d_array_with_nan = example_float_1d_array.copy()
    float_1d_array_with_nan[0] = np.nan
    float_1d_array_with_nan[len(float_1d_array_with_nan) // 2] = np.nan
    float_1d_array_with_nan[-1] = np.nan
    return float_1d_array_with_nan


# ======= 2D data as numpy arrays =======


@pytest.fixture(scope="session")
def example_int_2d_array(fixed_seed_random_generator) -> np.typing.NDArray:
    """
    Provides a 10x10 NumPy array of random integers in [0, 256).
    """
    return fixed_seed_random_generator.integers(0, 256, (10, 10))


@pytest.fixture(scope="session")
def example_float_2d_array(fixed_seed_random_generator) -> np.typing.NDArray:
    """
    Provides a 10x10 NumPy array of random floats in [0, 1).
    """
    return fixed_seed_random_generator.random((10, 10))


@pytest.fixture(scope="session")
def example_string_2d_array() -> np.typing.NDArray:
    """
    Provides a 2D NumPy array (4x5) of sample strings.
    """
    return np.array(
        [["a", "b", "c", "d", "e"], ["f", "g", "h", "i", "j"], ["k", "l", "m", "n", "o"], ["p", "q", "r", "s", "t"]]
    )


@pytest.fixture(scope="session")
def example_float_2d_array_with_nan(example_float_2d_array) -> np.typing.NDArray:
    """
    Provides a copy of a float 2D NumPy array with NaNs injected at the top-left, center, and bottom-right.
    Useful for testing NaN handling in 2D data.
    """
    float_2d_array_with_nan = example_float_2d_array.copy()
    float_2d_array_with_nan[(0, 0)] = np.nan
    float_2d_array_with_nan[(len(float_2d_array_with_nan) // 2, len(float_2d_array_with_nan) // 2)] = np.nan
    float_2d_array_with_nan[(-1, -1)] = np.nan
    return float_2d_array_with_nan


# ======= 1D data as python list =======


@pytest.fixture(scope="session")
def example_int_1d_list() -> List[int]:
    """
    Provides a 1D list of 10 random integers in [0, 255] with fixed seed.
    """
    random.seed(42)
    return [random.randint(0, 255) for _ in range(10)]


@pytest.fixture(scope="session")
def example_float_1d_list() -> List[float]:
    """
    Provides a 1D list of 10 random float values in [0, 1) with fixed seed.
    """
    random.seed(42)
    return [random.random() for _ in range(10)]


@pytest.fixture(scope="session")
def example_string_1d_list() -> List[str]:
    """
    Provides a 1D list of sample string values.
    """
    return ["a", "b", "c", "d", "e"]


@pytest.fixture(scope="session")
def example_int_1d_list_with_none(example_int_1d_list) -> List[Union[int, None]]:
    """
    Provides a copy of the int list with None values at the start, middle, and end.
    """
    int_1d_list_with_none = example_int_1d_list.copy()
    int_1d_list_with_none[0] = None
    int_1d_list_with_none[len(int_1d_list_with_none) // 2] = None
    int_1d_list_with_none[-1] = None
    return int_1d_list_with_none


@pytest.fixture(scope="session")
def example_float_1d_list_with_none(example_float_1d_list) -> List[Union[float, None]]:
    """
    Provides a copy of the float list with None values at the start, middle, and end.
    """
    float_1d_list_with_none = example_float_1d_list.copy()
    float_1d_list_with_none[0] = None
    float_1d_list_with_none[len(float_1d_list_with_none) // 2] = None
    float_1d_list_with_none[-1] = None
    return float_1d_list_with_none


@pytest.fixture(scope="session")
def example_string_1d_list_with_none(example_string_1d_list) -> List[Union[str, None]]:
    """
    Provides a copy of the string list with None values at the start, middle, and end.
    """
    string_1d_list_with_none = example_string_1d_list.copy()
    string_1d_list_with_none[0] = None
    string_1d_list_with_none[len(string_1d_list_with_none) // 2] = None
    string_1d_list_with_none[-1] = None
    return string_1d_list_with_none


# ======= 2D data as python list =======


@pytest.fixture(scope="session")
def example_int_2d_list() -> List[List[int]]:
    """
    Provides a 2D list (10x10) of random integers in [0, 255] with fixed seed.
    """
    random.seed(42)
    return [[random.randint(0, 255) for _ in range(10)] for _ in range(10)]


@pytest.fixture(scope="session")
def example_float_2d_list() -> List[List[float]]:
    """
    Provides a 2D list (10x10) of random float values in [0, 1) with fixed seed.
    """
    random.seed(42)
    return [[random.random() for _ in range(10)] for _ in range(10)]


@pytest.fixture(scope="session")
def example_string_2d_list() -> List[List[str]]:
    """
    Provides a 2D list of sample string values (4x5 grid).
    """
    return [["a", "b", "c", "d", "e"], ["f", "g", "h", "i", "j"], ["k", "l", "m", "n", "o"], ["p", "q", "r", "s", "t"]]


@pytest.fixture(scope="session")
def example_int_2d_list_with_none(example_int_2d_list) -> List[List[Union[int, None]]]:
    """
    Provides a copy of the 2D int list with None values injected at the top-left, center, and bottom-right.
    """
    int_2d_list_with_none = example_int_2d_list.copy()
    int_2d_list_with_none[0][0] = None
    int_2d_list_with_none[len(int_2d_list_with_none) // 2][len(int_2d_list_with_none) // 2] = None
    int_2d_list_with_none[-1][-1] = None
    return int_2d_list_with_none


@pytest.fixture(scope="session")
def example_float_2d_list_with_none(example_float_2d_list) -> List[List[Union[float, None]]]:
    """
    Provides a copy of the 2D float list with None values injected at the top-left, center, and bottom-right.
    """
    float_2d_list_with_none = example_float_2d_list.copy()
    float_2d_list_with_none[0][0] = None
    float_2d_list_with_none[len(example_float_2d_list) // 2][len(example_float_2d_list) // 2] = None
    float_2d_list_with_none[-1][-1] = None
    return float_2d_list_with_none


@pytest.fixture(scope="session")
def example_string_2d_list_with_none(example_string_2d_list) -> List[List[Union[str, None]]]:
    """
    Provides a copy of the 2D string list with None values injected at the top-left, center, and bottom-right.
    """
    string_2d_list_with_none = example_string_2d_list.copy()
    string_2d_list_with_none[0][0] = None
    string_2d_list_with_none[len(string_2d_list_with_none) // 2][len(string_2d_list_with_none) // 2] = None
    string_2d_list_with_none[-1][-1] = None
    return string_2d_list_with_none


# ======= Additional metadata =======


@pytest.fixture(scope="session")
def example_metadata(fixed_seed_random_generator):
    """
    Provides a sample metadata dictionary with mixed types, including NumPy arrays.
    Useful for testing metadata compatibility and serialization.
    """
    return {
        "str metadata": "I'm a string metadata",
        "float metadata": 1.5,
        "int metadata": 42,
        "list metadata": [1, 2, 3, 4, 5],
        "numpy array metadata": fixed_seed_random_generator.integers(0, 10, 5),
    }


@pytest.fixture(scope="session")
def example_unit():
    """
    Provides a sample unit string representing a measurement unit.
    """
    return "Some measurement unit"


# ======= Assonant Entries =======


@pytest.fixture(scope="function")
def example_entry():
    return AssonantEntryFactory.create_entry(beamline_name=BeamlineName.CARNAUBA, name="entry")


# ======= Assonant Components =======
# Allow abstracting creation.
# Useful when testing different data types is not needed.


@pytest.fixture(scope="function")
def example_base_component():
    return AssonantComponentFactory.create_component_by_class_type(Component, "main_component")


@pytest.fixture(scope="function")
def example_subcomponent():
    return AssonantComponentFactory.create_component_by_class_type(Component, "subcomponent")


@pytest.fixture(scope="function")
def example_translation_axis(example_float_1d_array, example_unit, example_metadata):
    return AssonantDataHandlerFactory.create_axis(
        transformation_type=TransformationType.TRANSLATION,
        value=example_float_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
    )


@pytest.fixture(scope="function")
def example_rotation_axis(example_float_1d_array, example_unit, example_metadata):
    return AssonantDataHandlerFactory.create_axis(
        transformation_type=TransformationType.ROTATION,
        value=example_float_1d_array,
        unit=example_unit,
        extra_metadata=example_metadata,
    )


@pytest.fixture(scope="function")
def example_int_1d_array_data_field(example_int_1d_array, example_unit, example_metadata):
    return AssonantDataHandlerFactory.create_data_field(
        value=example_int_1d_array, unit=example_unit, extra_metadata=example_metadata
    )


@pytest.fixture(scope="function")
def example_float_2d_array_data_field(example_float_2d_array, example_unit, example_metadata):
    return AssonantDataHandlerFactory.create_data_field(
        value=example_float_2d_array, unit=example_unit, extra_metadata=example_metadata
    )


@pytest.fixture(scope="function")
def example_string_data_field(example_string_value, example_unit, example_metadata):
    return AssonantDataHandlerFactory.create_data_field(
        value=example_string_1d_array, unit=example_unit, extra_metadata=example_metadata
    )
