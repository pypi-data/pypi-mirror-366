from yta_general_utils.math.value_normalizer import ValueNormalizer
from yta_validation.parameter import ParameterValidator
from yta_validation.number import NumberValidator
from yta_validation import PythonValidator
from yta_random import Random
from typing import Union

import numpy as np


COORDINATE_MAX_POSITION = (1920 * 4, 1080 * 4)
"""
The maximum accepted position for a coordinate.
This position will be used for validation and
for normalization.
"""
COORDINATE_MIN_POSITION = (-COORDINATE_MAX_POSITION[0], -COORDINATE_MAX_POSITION[1])
"""
The minimum accepted position for a coordinate.
This position will be used for validation and
for normalization.
"""



# TODO: This is the new Coordinate class we want to keep
# when we know it is working properly
class Coordinate:
    """
    Class to represent a point, a position, in a graphic
    defined by both X and Y axis. This coordinate exist
    in our defined virtual limits and it is useful to
    position images or videos within a scene.

    This class is able to normalize and denormalize its
    values according to the scenario.
    """

    position: tuple[float, float] = None
    """
    The coordinate position not normalized. The X and
    Y axis values are within our specific limits 
    defined in this file.
    """

    @property
    def x(
        self
    ):
        return self.position[0]
    
    @property
    def y(
        self
    ):
        return self.position[1]
    
    @property
    def normalized_position(
        self
    ):
        """
        The coordinate position but normalized, meaning
        that the X and Y axis are values within the
        [0, 1] range.
        """
        if not hasattr(self, '_normalized_position'):
            value_normalizer = ValueNormalizer(COORDINATE_MIN_POSITION, COORDINATE_MAX_POSITION)

            self._normalized_position = (
                value_normalizer.normalize(self.x),
                value_normalizer.normalize(self.y)
            )

        return self._normalized_position
    
    @property
    def x_normalized(
        self
    ):
        return self.normalized_position[0]
    
    @property
    def y_normalized(
        self
    ):
        return self.normalized_position[1]
    
    @property
    def as_tuple(
        self
    ):
        """
        Return the coordinate as a not normalized tuple
        ('x', 'y').
        """
        return (
            self.x,
            self.y
        )
    
    @property
    def as_tuple_normalized(
        self
    ):
        """
        Return the coordinate as a normalized tuple
        ('x', 'y').
        """
        return (
            self.x_normalized,
            self.y_normalized
        )
    
    @property
    def as_array(
        self
    ):
        """
        Return the coordinate as a not normalized array
        ['x', 'y'].
        """
        return [
            self.x,
            self.y
        ]
    
    @property    
    def as_array_normalized(
        self
    ):
        """
        Return the coordinate as a normalized array
        ['x', 'y'].
        """
        return [
            self.x_normalized,
            self.y_normalized
        ]
    
    def __init__(
        self,
        position: Union[tuple[int, int], list[int, int]],
        is_normalized: bool = False
    ):
        validate_coordinate_position(position, is_normalized)

        value_normalizer = ValueNormalizer(COORDINATE_MIN_POSITION, COORDINATE_MAX_POSITION)

        position = (
            value_normalizer.denormalize(position[0]),
            value_normalizer.denormalize(position[1])
        ) if is_normalized else (
            position[0],
            position[1]
        )
        
        self.position = position
    
    @staticmethod
    def generate(
        n: int = 1,
        lower_limit: Union[tuple[int, int], list[int, int]] = (0, 0),
        upper_limit: Union[tuple[int, int], list[int, int]] = (1920, 1080)
    ):
        """
        Generate 'n' coordinates with random values
        between the 'lower_limit' and the 'upper_limit'
        that are returned as an array of instances.

        The 'n', which is the amount of coordinates to create,
        is limited to the interval [1, 100].
        """
        ParameterValidator.validate_int_between('n', n, 1, 100)
        
        # This is not actually a coordinate position but
        # a coordinate limit, so it works similar
        validate_coordinate_position(lower_limit)
        validate_coordinate_position(upper_limit)
        
        return [
            Coordinate((
                Random.int_between(lower_limit[0], upper_limit[0]),
                Random.int_between(lower_limit[1], upper_limit[1])
            ))
            for _ in range(n)
        ]

# TODO: Remove this Coordinate when the one above
# has been refactored and it is working perfectly

NORMALIZATION_MIN_VALUE = -10_000
"""
The lower limit for the normalization process.
"""
NORMALIZATION_MAX_VALUE = 10_000
"""
The upper limit for the normalization process.
"""

# TODO: Is Coordinate class actually needed (?)
# class Coordinate:
#     """
#     Class to represent a coordinate point ('x', 'y').
#     """
#     position: tuple = None
#     """
#     The ('x', 'y') tuple containing the position
#     coordinate.
#     """
#     _is_normalized: bool = False
#     """
#     Internal function to know if it has been normalized
#     or not.
#     """

#     @property
#     def x(self):
#         return self.position[0]
    
#     @property
#     def y(self):
#         return self.position[1]
    
#     @property
#     def is_normalized(self):
#         return self._is_normalized

#     def __init__(self, x: float, y: float, is_normalized: bool = False):
#         if not NumberValidator.is_number_between(x, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE) or not NumberValidator.is_number_between(y, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE):
#             raise Exception(f'The "x" and "y" parameters must be values between {str(NORMALIZATION_MIN_VALUE)} and {str(NORMALIZATION_MAX_VALUE)} and "{str(x)}, {str(y)}" provided.')
        
#         if not PythonValidator.is_boolean(is_normalized):
#             raise Exception('The "is_normalized" parameter must be a boolean value.')
        
#         self.position = (x, y)
#         self._is_normalized = is_normalized

#     def get_x(self):
#         """
#         Return the 'x' value.
#         """
#         return self.x
    
#     def get_y(self):
#         """
#         Return the 'y' value.
#         """
#         return self.y

#     def as_tuple(self):
#         """
#         Return the coordinate as a tuple ('x', 'y').
#         """
#         return Coordinate.to_tuple(self)
    
#     def as_array(self):
#         """
#         Return the coordinate as an array ['x', 'y'].
#         """
#         return Coordinate.to_array(self)

#     def normalize(self):
#         """
#         Normalize the coordinate by turning the values into
#         a range between [0.0, 1.0]. This will be done if the
#         values have not been normalized previously.
#         """
#         if not self._is_normalized:
#             self.position = Coordinate.normalize_tuple(self.position)
#             self._is_normalized = True

#         return self

#     def denormalize(self):
#         """
#         Denormalize the coordinate values by turning them
#         from normalized values to the real ones. This will
#         be done if the values have been normalized 
#         previously.
#         """
#         if self._is_normalized:
#             self.position = Coordinate.denormalize_tuple(self.position)
#             self._is_normalized = False

#         return self

#     @staticmethod
#     def to_tuple(coordinate):
#         """
#         Turn the provided 'coordinate' to a tuple like ('x', 'y').
#         """
#         return coordinate.position
    
#     @staticmethod
#     def to_array(coordinate):
#         """
#         Turn the provided 'coordinate' to an array like ['x', 'y'].
#         """
#         return [coordinate.x, coordinate.y]

#     @staticmethod
#     def generate(amount: int = 1):
#         """
#         Generate 'amount' coordinates with random values
#         between [0, 1920] for the 'x' and [0, 1080] for
#         the 'y', that are returned as an array of instances.

#         The 'amount' parameter is limited to the interval 
#         [1, 100].
#         """
#         if not NumberValidator.is_number_between(amount, 1, 100):
#             raise Exception(f'The provided "amount" parameter "{str(amount)}" is not a number between 1 and 100.')
        
#         return Coordinate(random_int_between(0, 1920), random_int_between(0, 1080))
    
#     @staticmethod
#     def to_numpy(coordinates: list['Coordinate']):
#         """
#         Convert a list of Coordinates 'coordinates' to
#         numpy array to be able to work with them.

#         This method does the next operation:
#         np.array([[coord.x, coord.y] for coord in coordinates])
#         """
#         if not PythonValidator.is_list(coordinates):
#             if not PythonValidator.is_instance_of(coordinates, Coordinate):
#                 raise Exception('The provided "coordinates" parameter is not a list of NormalizedCoordinates nor a single NormalizedCoordinate instance.')
#             else:
#                 coordinates = [coordinates]
#         elif any(not PythonValidator.is_instance_of(coordinate, Coordinate) for coordinate in coordinates):
#             raise Exception('At least one of the provided "coordinates" is not a NormalizedCoordinate instance.')

#         return np.array([coordinate.as_array() for coordinate in coordinates])
    
#     @staticmethod
#     def normalize_tuple(coordinate: tuple):
#         """
#         Normalize the provided 'coordinate' by applying
#         our normalization limits. This means turning the
#         non-normalized 'coordinate' to a normalized one
#         (values between 0.0 and 1.0).
#         """
#         return (
#             Math.normalize(coordinate[0], NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE),
#             Math.normalize(coordinate[1], NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE)
#         )
    
#     @staticmethod
#     def denormalize_tuple(coordinate: tuple):
#         """
#         Denormalize the provided 'coordinate' by applying
#         our normalization limits. This means turning the 
#         normalized 'coordinate' (values between 0.0 and
#         1.0) to the not-normalized ones according to our
#         normalization limits.
#         """
#         return (
#             Math.denormalize(coordinate[0], NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE),
#             Math.denormalize(coordinate[1], NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE)
#         )
    
#     @staticmethod
#     def is_valid(coordinate: tuple):
#         """
#         Check if the provided 'coordinate' is valid or not.
#         A valid coordinate is a tuple with two elements that
#         are values between our normalization limits.
#         """
#         if not PythonValidator.is_instance_of(coordinate, 'Coordinate') and (not PythonValidator.is_tuple(coordinate) or len(coordinate) != 2 or not NumberValidator.is_number_between(coordinate[0], NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE) or not NumberValidator.is_number_between(coordinate[1], NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE)):
#             return False
        
#         return True

#     @staticmethod
#     def validate(coordinate: tuple, parameter_name: str):
#         """
#         Validate if the provided 'coordinate' is a coordinate
#         with values between our normalization limits.
#         """
#         if not Coordinate.is_valid(coordinate):
#             raise Exception(f'The provided "{parameter_name}" parameter is not a valid tuple of 2 elements that are values between our limits {str(NORMALIZATION_MIN_VALUE)} and {str(NORMALIZATION_MAX_VALUE)}. Please, provide a valid coordinate.')


def validate_coordinate_position(position: Union[tuple[int, int], list[int, int]], is_normalized: bool = False):
    """
    Validate if a coordinate position is a tuple or list
    of 2 elements within our valid range.
    """
    if (not PythonValidator.is_tuple(position) and not PythonValidator.is_list(position)) or len(position) != 2:
        raise Exception('The provided "position" parameter is not a tuple nor a list of 2 elements.')
    
    if is_normalized:
        if not NumberValidator.is_number_between(position[0], 0, 1) or not NumberValidator.is_number_between(position[1], 0, 1):
            raise Exception(f'The provided "position" ({position[0], position[1]}) is out of the normalized range, which is from (0, 0) to (1, 1)')
    else:
        if not NumberValidator.is_number_between(position[0], COORDINATE_MIN_POSITION[0], COORDINATE_MAX_POSITION[0]) or not NumberValidator.is_number_between(position[1], COORDINATE_MIN_POSITION[1], COORDINATE_MAX_POSITION[1]):
            raise Exception(f'The provided "position" ({position[0], position[1]}) is out of range, which is from ({COORDINATE_MIN_POSITION[0]}, {COORDINATE_MIN_POSITION[1]}) to ({COORDINATE_MAX_POSITION[0]}, {COORDINATE_MAX_POSITION[1]})')

def coordinates_to_numpy(coordinates: list['Coordinate']):
    """
    Convert a list of Coordinates 'coordinates' to
    numpy array to be able to work with them.

    This method does the next operation:
    np.array([[coord.x, coord.y] for coord in coordinates])
    """
    if not PythonValidator.is_list(coordinates):
        if not PythonValidator.is_instance_of(coordinates, Coordinate):
            raise Exception('The provided "coordinates" parameter is not a list of NormalizedCoordinates nor a single NormalizedCoordinate instance.')
        else:
            coordinates = [coordinates]
    elif any(not PythonValidator.is_instance_of(coordinate, Coordinate) for coordinate in coordinates):
        raise Exception('At least one of the provided "coordinates" is not a NormalizedCoordinate instance.')

    return np.array([coordinate.as_array() for coordinate in coordinates])