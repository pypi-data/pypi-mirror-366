from yta_positioning.coordinate import Coordinate
from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from yta_general_utils.math.rate_functions.rate_function import RateFunction
from yta_general_utils.math.normalizable_value import NormalizableValue
from yta_general_utils.math.progression import Progression
from yta_validation.parameter import ParameterValidator


# This class is very similar to PairOfNodes, maybe
# we can do something to avoid the duplicated code
class PairOfCoordinates:
    """
    Class to represent a par of coordinates that
    belong to a Map instance.
    """

    first_coordinate: Coordinate = None
    second_coordinate: Coordinate = None
    rate_function: RateFunctionArgument = None

    @property
    def max_x(
        self
    ):
        """
        The maximum X value, which can be the left coordinate
        or right coordinate X value.
        """
        return max([self.first_coordinate.x, self.second_coordinate.x])
    
    @property
    def min_x(
        self
    ):
        """
        The minimum X value, which can be the left coordinate
        or right coordinate X value.
        """
        return min([self.first_coordinate.x, self.second_coordinate.x])
    
    @property
    def max_y(
        self
    ):
        """
        The maximum Y value, which can be the left coordinate
        or right coordinate Y value.
        """
        return max([self.first_coordinate.y, self.second_coordinate.y])
    
    @property
    def min_y(
        self
    ):
        """
        The minimum Y value, which can be the left coordinate
        or right coordinate Y value.
        """
        return min([self.first_coordinate.y, self.second_coordinate.y])
    
    @property
    def is_backwards(
        self
    ):
        """
        Check if the X value of the first coordinate is
        greater than the X value of the second coordinate.
        If so, the pair of coordinates is backwards (in X
        value, as it is decreasing when going from first
        coordinate to second coordinate).
        """
        return self.first_coordinate.x > self.second_coordinate.x

    @property
    def is_descendant(
        self
    ):
        """
        Check if the Y value of the first coordinate is
        greater than the Y value of the second coordinate.
        If so, the pair of coordinates is descendant (in
        Y value, as it is decreasing when going from first
        coordinate to second coordinate).
        """
        return self.first_coordinate.y > self.second_coordinate.y

    def __init__(
        self,
        first_coordinate: Coordinate,
        second_coordinate: Coordinate,
        rate_function: RateFunctionArgument = RateFunctionArgument(RateFunction.EASE_IN_OUT_SINE)
    ):
        self.first_coordinate = first_coordinate
        self.second_coordinate = second_coordinate
        self.rate_function = rate_function
    
    def get_xy_from_normalized_local_d(
        self,
        d: float
    ):
        """
        The 'd' parameter must be the local distance within
        this pair of coordinates, that would have been
        calculated from a global map 'd' distance.

        This is the only implemented method because there is
        a floating decimal bug that, when converted to an X
        value, is sometimes out of the limits and raising
        Exception. Using a local 'd' is a better way to make
        sure the X obtained fits the range limit.
        """
        x = self.first_coordinate.x + d * (self.second_coordinate.x - self.first_coordinate.x)
        
        return (
            x,
            self._get_y_from_x(x, is_x_normalized = False).value
        )
    
    def get_n_xy_values_to_plot(
        self,
        n: int = 100,
        do_normalize: bool = False
    ) -> list[tuple[NormalizableValue, NormalizableValue]]:
        """
        Return 'n' (x, y) values to be plotted. Each of those
        X and Y values are normalized only if 'do_normalize'
        flag parameter is set as True.
        """
        ParameterValidator.validate_mandatory_positive_number('n', n, do_include_zero = False)
        
        n = int(n)

        xs = [
            NormalizableValue(x, (self.min_x, self.max_x))
            for x in Progression(self.min_x, self.max_x, 100, RateFunctionArgument.default()).values
        ]
        ys = [
            self._get_y_from_x(x.value, is_x_normalized = False)
            for x in xs
        ]

        if do_normalize:
            xs = [
                x.normalized
                for x in xs
            ]
            ys = [
                y.normalized
                for y in ys
            ]
        else:
            xs = [
                x.value
                for x in xs
            ]
            ys = [
                y.value
                for y in ys
            ]

        return list(zip(xs, ys))
    
    def _get_y_from_x(
        self,
        x: float,
        is_x_normalized: bool = False
    ) -> NormalizableValue:
        """
        Get the Y value for the given X, depending on if
        the X value is normalized or not, flagged with the
        'is_x_normalized' parameter.
        
        This method is for internal use only.
        """
        lower_limit = (
            self.min_x
            if not is_x_normalized else
            0
        )
        upper_limit = (
            self.max_x
            if not is_x_normalized else
            1
        )

        # I round the 'x' here to avoid floating decimal issue
        x = round(x)

        ParameterValidator.validate_mandatory_number_between('x', x, lower_limit, upper_limit)
        
        value = NormalizableValue(x, (self.min_x, self.max_x), value_is_normalized = is_x_normalized)
        # TODO: I think if first x is greater than second x here
        # I must do 1 - self.rate_function.get_n_value(value.normalized)
        # c1(400, 20), c2(300, 10), x = 340
        # 340 normalized is 0.4 [300, 400], but as we are from 400
        # to 300 it should be d=0.6
        value = (
            NormalizableValue(self.rate_function.get_n_value(1 - value.normalized
            if self.is_backwards else
            value.normalized), (self.min_y, self.max_y), value_is_normalized = True)
        )
        value = (
            NormalizableValue(1 - value.normalized, (self.min_y, self.max_y), value_is_normalized = True)
            if self.is_descendant else
            value
        )

        return value