"""
THIS IS VERY IMPORTANT TO UNDERSTAND THE CODE:

- First of all, the distance. Imagine the map
once it's been plotted. If you go from the origin
to the end, there is a distance you are virtually
drawing. That is the global distance. The distance
from the origin, normalized, is d=1.0. The origin
is d=0.0 and the end is d=1.0.

- As you are using pairs of coordinates, there is
also a local distance in between each pair of
coordinates. Imagine, for a second, that each pair
of coordinates is a map by itself. The first 
coordinate is the d=0.0 and the second coordinate
is the d=1.0 (in local distance terms).

- If you have, for example, 5 pairs of coordinates,
as the total global distance is d=1.0, each pair of
coordinates will represent a 1/5 of that total
global distance, so each pair of coordinates 
local distance is a 1/5 = 0.2 of the total global
distance. Knowing that, in order, the pairs of
coordinates represent the global distance as
follows: [0.0, 0.2], (0.2, 0.4], (0.4, 0.6],
(0.6, 0.8] and (0.8, 1.0] (for the same example
with 5 pairs of coordinates).

- Now that you have clear the previous steps, if
you think about a global distance of d=0.3, that
will be in the second pair of coordinates (the
one that represents (0.2, 0.4] range. But that
d=0.3 is in terms of global distance, so we need
to adapt it to that pair of coordinates local
distance. As we skipped 1 (the first) pair of
coordinates, we need to substract its distance
representation from our global distance, so
d=0.3 - 0.2 => d=0.1. Now, as d=0.1 is a global
distance value, we need to turn it into a local
distance value. As each pair of coordinates
represents a 0.2 of the global distance, we do
this: d=0.1 / 0.2 => d=0.5 and we obtain a local
distance of d=0.5. That is the local distance
within the second pair of coordinates (in this
example) we need to look for.

- Once we know the local distance we need to 
look for, as we now the pair of coordinates X
value of each of those coordinates, we can 
calculate the corresponding X value for what
that local distance fits.

As you can see, we go from a global distance to
a local X value to obtain the corresponding Y
of the affected pair of coordinates. This class
has been created with the purpose of following
a movement, so the distance we are talking about
is actually the amount of that movement we have
done previously so we can obtain the next 
position to which we need to move to follow the
movement that this map describes.
"""
from yta_positioning.coordinate import Coordinate, validate_coordinate_position
from yta_positioning.map.pair_of_coordinates import PairOfCoordinates
from yta_general_utils.math.progression import Progression
from yta_programming.decorators.requires_dependency import requires_dependency
from typing import Union


# TODO: I think this is not actually a Map so the
# class name should change as it is more a Movement
# graphic and the Graphic class is an Animation
# Graphic or something like that
class Map:
    """
    A class to represent an scenario in which we will
    position Coordinates. The order of the coordinates
    will determine the direction of the movement, and
    they can be disordered (the next coordinate can be
    in a lower X and Y position). Also, there can be
    different coordinates in the same position.

    This is useful to simulate the movement within a
    scene.
    """
    
    coordinates: list[Coordinate] = None

    @property
    def pairs_of_coordinates(
        self
    ) -> list[PairOfCoordinates]:
        """
        Get pairs of coordinates ordered by the moment in which
        they were added to the map. There is, at least, one pair
        of coordinates that will be, if no more coordinates
        added, the first and the last one.
        """
        return [
            PairOfCoordinates(self.coordinates[index], self.coordinates[index + 1])
            for index, _ in enumerate(self.coordinates[1:])
        ]

    @property
    def min_x(
        self
    ):
        return min(self.coordinates, key = lambda coordinate: coordinate.x).x

    @property
    def max_x(
        self
    ):
        return max(self.coordinates, key = lambda coordinate: coordinate.x).x
    
    @property
    def min_y(
        self
    ):
        return min(self.coordinates, key = lambda coordinate: coordinate.y).y

    @property
    def max_y(
        self
    ):
        return max(self.coordinates, key = lambda coordinate: coordinate.y).y

    def __init__(
        self
    ):
        self.coordinates = []

    def add_coordinate(
        self,
        position: Union[tuple[float, float], list[float]]
    ):
        """
        Add a new coordinate to the map if valid. The
        coordinate added can be in the same position as
        another coordinate.
        
        This method returns the instance so you can chain
        more than one 'add_coordinate' method call.
        """
        # TODO: Maybe accept Coordinate instance also
        # validating its position
        validate_coordinate_position(position)

        self.coordinates.append(Coordinate(position))

        return self
    
    def get_n_values(
        self,
        n: int
    ):
        """
        Return a list of 'n' (x, y) values of the map
        from the start to the end of it.
        """
        return [
            self.get_xy_from_normalized_global_d(d)
            for d in Progression(0, 1, n).values
        ]
    
    def get_xy_from_normalized_global_d(
        self,
        d: float
    ):
        """
        Return a not normalized tuple (x, y) representing
        the position for the provided global distance 'd',
        that is the global distance in the whole graphic X
        axis. The 'x' value of the first coordinate of the
        would be d=0.0 and the 'x' value of the last 
        coordinate, d=1.0.
        """
        # I'm using only this method as public method
        # because the 'd' global value is the only one that
        # lets me calculate the 'x' without a rounding
        # error.
        pair_of_coordinates = self._get_pair_of_coordinates_from_normalized_global_d(d)

        return pair_of_coordinates.get_xy_from_normalized_local_d(self._get_normalized_local_d_from_normalized_global_d(d))

    # Helpers below
    # TODO: Many helpers. Necessary (?)
    def _get_pair_of_coordinates_d(self):
        """
        Get the global distance 'd' that each pair of
        coordinates occupy.
        """
        return 1 / len(self.pairs_of_coordinates)
    
    def _get_pair_of_coordinates_index_from_normalized_global_d(
        self,
        d: float
    ):
        """
        The 'd' is a global normalized distance value.
        """
        return (
            int(d // self._get_pair_of_coordinates_d())
            if d != 1.0 else
            len(self.pairs_of_coordinates) - 1
        )
    
    def _get_pair_of_coordinates_from_normalized_global_d(
        self,
        d: float
    ):
        """
        Look for the pair of coordinates corresponding to
        the given global distance 'd' value.
        """
        pair_of_coordinates_index = self._get_pair_of_coordinates_index_from_normalized_global_d(d)

        return self.pairs_of_coordinates[pair_of_coordinates_index]

    def _get_normalized_local_d_from_normalized_global_d(
        self,
        d: float
    ):
        """
        Transform the global 'd' to a local 'd' that would
        be in the corresponding pair of coordinates.
        """
        pair_of_coordinates_index = self._get_pair_of_coordinates_index_from_normalized_global_d(d)
        pair_of_coordinates_d = self._get_pair_of_coordinates_d()

        if d != 1.0:
            d = (
                d % (pair_of_coordinates_index * pair_of_coordinates_d) / pair_of_coordinates_d
                if pair_of_coordinates_index > 0 else
                d / pair_of_coordinates_d
            )

        return d
    # Helpers above
    
    @requires_dependency('matplotlib', 'yta_general_utils', 'matplotlib')
    def plot(
        self
    ):
        """
        This method needs the next library:
        - `matplotlib`
        """
        import matplotlib.pyplot as plt

        # Limit and draw axis
        # plt.xlim(self.min_x, self.max_x)
        # plt.ylim(self.min_y, self.max_y)
        plt.xlim(0, 1920)
        plt.ylim(0, 1080)
        plt.axhline(0, color = 'black', linewidth = 1)
        plt.axvline(0, color = 'black', linewidth = 1)

        plt.grid(True)

        # Draw nodes
        x_vals = [
            coordinate.x
            for coordinate in self.coordinates
        ]
        y_vals = [
            coordinate.y
            for coordinate in self.coordinates
        ]
        plt.scatter(x_vals, y_vals, color = 'white', edgecolors = 'black', s = 100)

        # Draw points between nodes
        xs = []
        ys = []
        for pair_of_coordinates in self.pairs_of_coordinates:
            positions = pair_of_coordinates.get_n_xy_values_to_plot(100)
            t_xs, t_ys = zip(*positions)
            xs += t_xs
            ys += t_ys
       
        plt.scatter(xs, ys, color = 'black', s = 1)

        # Ploting is from bottom-left to top-right while moviepy
        # scenario is from top-left to bottom-right. We need to
        # invert the Y axis to see the graphic as the movement
        plt.gca().invert_yaxis()
        
        plt.title('')
        plt.xlabel('X axis')
        plt.ylabel('Y axis')
        
        plt.show()