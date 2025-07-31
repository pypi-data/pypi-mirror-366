from yta_positioning.coordinate import NORMALIZATION_MAX_VALUE, NORMALIZATION_MIN_VALUE
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from typing import Union


def is_size_valid(
    size: Union[tuple, list]
):
    """
    Check if the provided 'size' is a valid
    value or not, which means that is a tuple,
    list or array of 2 elements that are
    between the expected values.
    """
    return PythonValidator.is_numeric_tuple_or_list_or_array_of_2_elements_between_values(size, 1, NORMALIZATION_MAX_VALUE, 1, NORMALIZATION_MAX_VALUE)

def validate_size(
    size: tuple,
    parameter_name: str = 'size'
):
    """
    Validate the provided 'size' and raises an Exception if
    not valid.
    """
    ParameterValidator.validate_mandatory_numeric_tuple_or_list_or_array_of_2_elements_between_values(parameter_name, size, 1, NORMALIZATION_MAX_VALUE, 1, NORMALIZATION_MAX_VALUE)

def is_position_valid(
    position: Union[list, tuple]
):
    """
    It is a list or tuple of 2 values which are between
    our min and max normalization values.
    """
    return PythonValidator.is_numeric_tuple_or_list_or_array_of_2_elements_between_values(position, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE)

def validate_position(
    position: Union[list, tuple],
    parameter_name: str = 'position'
):
    """
    Validate if the given 'position' is a valid position,
    which must be a tuple or array of 2 elements between
    our min and max normalization values.
    """
    ParameterValidator.validate_mandatory_numeric_tuple_or_list_or_array_of_2_elements_between_values(parameter_name, position, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE)