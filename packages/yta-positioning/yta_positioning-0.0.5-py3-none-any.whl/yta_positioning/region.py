from yta_positioning.coordinate import Coordinate
from yta_validation.parameter import ParameterValidator
from dataclasses import dataclass


@dataclass
class Region:
    """
    Class to represent a region built by two
    coordinates, one in the top left corner
    and another one in the bottom right corner.
    """

    # TODO: Remove these values as they are from
    # the class and we use instances always
    top_left: Coordinate = None
    bottom_right: Coordinate = None
    # TODO: Do we actually need them (?)
    coordinates: list[Coordinate] = None
    width: int = None
    height: int = None

    def __init__(
        self,
        top_left_x: int,
        top_left_y: int,
        bottom_right_x: int,
        bottom_right_y: int,
        coordinates: list[Coordinate]
    ):
        ParameterValidator.validate_mandatory_int('top_left_x', top_left_x)
        ParameterValidator.validate_mandatory_int('top_left_y', top_left_y)
        ParameterValidator.validate_mandatory_int('bottom_right_x', bottom_right_x)
        ParameterValidator.validate_mandatory_int('bottom_right_y', bottom_right_y)
        ParameterValidator.validate_mandatory_list_of_these_instances('coordinates', coordinates, Coordinate)

        self.top_left = Coordinate(top_left_x, top_left_y)
        self.bottom_right = Coordinate(bottom_right_x, bottom_right_y)
        self.coordinates = coordinates
        self.width = self.bottom_right.x - self.top_left.x
        self.height = self.bottom_right.y - self.top_left.y

    @property
    def size_to_fit(
        self
    ) -> tuple[int, int]:
        """
        Size that guarantees any element fits the region.
        This includes a 1% of increase to make sure no
        black pixels are shown in the borders.
        """
        return (
            int(self.width * 1.01),
            int(self.height * 1.01)
        )
    
    @property
    def center(
        self
    ) -> tuple[int, int]:
        """
        The center position of the region represented by
        a tuple (x, y).
        """
        return (
            int(self.bottom_right.x - self.width / 2),
            int(self.bottom_right.y - self.height / 2)
        )
    
