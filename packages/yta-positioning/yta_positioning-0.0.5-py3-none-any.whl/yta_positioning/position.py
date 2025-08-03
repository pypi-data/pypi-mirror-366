from yta_positioning.validation import validate_size
from yta_positioning.coordinate import Coordinate
from yta_constants.multimedia import DEFAULT_SCENE_SIZE, DEFAULT_MANIM_SCENE_SIZE
from yta_constants.enum import YTAEnum as Enum
from random import choice as randchoice


class Position(Enum):
    """
    Enum class that represents a position within an specific
    scene. This is used to position a video or an image in that
    scene in an specific position defined by itself. It is
    useful with Manim and Moviepy video positioning and has
    been prepared to work with those engines.

    This position is always considered in a scene of 1920x1080.

    This position is a static position which means that it can
    be calculated by itself, without the need of any element
    size or similar. The coordinate that represent any of this
    """

    CENTER = 'center'
    """
    Just on the center of the scene
    """
    IN_EDGE_TOP = 'in_edge_top'
    """
    Just on the top edge of the scene.
    """
    IN_EDGE_BOTTOM = 'in_edge_bottom'
    IN_EDGE_RIGHT = 'in_edge_right'
    IN_EDGE_LEFT = 'in_edge_left'

    IN_EDGE_TOP_LEFT = 'in_edge_top_left'
    """
    Just on the upper left edge corner of the scene.
    """
    IN_EDGE_TOP_RIGHT = 'in_edge_top_right'
    IN_EDGE_BOTTOM_RIGHT = 'in_edge_bottom_right'
    IN_EDGE_BOTTOM_LEFT = 'in_edge_bottom_left'

    HALF_LEFT = 'half_left'
    """
    Between the left edge and the center of the scene.
    """
    HALF_TOP_LEFT = 'half_top_left'
    HALF_TOP = 'half_top'
    HALF_TOP_RIGHT = 'half_top_right'
    HALF_RIGHT = 'half_right'
    HALF_BOTTOM_RIGHT = 'half_bottom_right'
    HALF_BOTTOM = 'half_bottom'
    HALF_BOTTOM_LEFT = 'half_bottom_left'

    OUT_LEFT = 'out_left'
    """
    Imagine our scene surrounded by another 8 scenes.
    This will be at the center that surrounding scene
    that is on the left of this one.
    """
    OUT_TOP = 'out_top'
    """
    Imagine our scene surrounded by another 8 scenes.
    This will be at the center that surrounding scene
    that is on the top of this one.
    """
    OUT_RIGHT = 'out_right'
    """
    Imagine our scene surrounded by another 8 scenes.
    This will be at the center that surrounding scene
    that is on the right of this one.
    """
    OUT_BOTTOM = 'out_bottom'
    """
    Imagine our scene surrounded by another 8 scenes.
    This will be at the center that surrounding scene
    that is on the bottom of this one.
    """
    OUT_TOP_LEFT = 'out_top_left'
    """
    Imagine our scene surrounded by another 8 scenes.
    This will be at the center that surrounding scene
    that is on the top and left of this one.
    """
    OUT_TOP_RIGHT = 'out_top_right'
    """
    Imagine our scene surrounded by another 8 scenes.
    This will be at the center that surrounding scene
    that is on the top and right of this one.
    """
    OUT_BOTTOM_LEFT = 'out_bottom_left'
    """
    Imagine our scene surrounded by another 8 scenes.
    This will be at the center that surrounding scene
    that is on the bottom and left of this one.
    """
    OUT_BOTTOM_RIGHT = 'out_bottom_right'
    """
    Imagine our scene surrounded by another 8 scenes.
    This will be at the center that surrounding scene
    that is on the bottom and right of this one.
    """
    RANDOM_INSIDE = 'random_inside'
    RANDOM_OUTSIDE = 'random_outside'

    @staticmethod
    def get_outside_elements_list(
    ) -> list['Position']:
        """
        Return all the positions that are outside of 
        the screen as a list.
        """
        return [
            Position.OUT_BOTTOM,
            Position.OUT_BOTTOM_LEFT,
            Position.OUT_BOTTOM_RIGHT,
            Position.OUT_RIGHT,
            Position.OUT_LEFT,
            Position.OUT_TOP,
            Position.OUT_TOP_LEFT,
            Position.OUT_TOP_RIGHT
        ]
    
    @staticmethod
    def get_inside_elements_list(
    ) -> list['Position']:
        """
        Return all the positions that are inside of the 
        screen as a list.
        """
        return [
            Position.CENTER,
            Position.IN_EDGE_TOP,
            Position.IN_EDGE_BOTTOM,
            Position.IN_EDGE_RIGHT,
            Position.IN_EDGE_LEFT,
            Position.IN_EDGE_TOP_LEFT,
            Position.IN_EDGE_TOP_RIGHT,
            Position.IN_EDGE_BOTTOM_RIGHT,
            Position.IN_EDGE_BOTTOM_LEFT,
            Position.HALF_LEFT,
            Position.HALF_TOP_LEFT,
            Position.HALF_TOP,
            Position.HALF_TOP_RIGHT,
            Position.HALF_RIGHT,
            Position.HALF_BOTTOM_RIGHT,
            Position.HALF_BOTTOM,
            Position.HALF_BOTTOM_LEFT
        ]

        # This below is not working, so I put it
        # manually by now...
        return list(set(Position.get_all()) - set(Position.get_outside_elements_list()) - set([Position.RANDOM_INSIDE]) - set([Position.RANDOM_OUTSIDE]))

    @staticmethod
    def get_random_outside(
    ) -> 'Position':
        """
        Return a random position which is outside of the
        screen.
        """
        return randchoice(Position.get_outside_elements_list())
    
    @staticmethod
    def get_random_inside(
    ) -> 'Position':
        """
        Return a random position which is inside of the
        screen.
        """
        return randchoice(Position.get_inside_elements_list())

    def get_moviepy_center_tuple(
        self,
        scene_size: tuple = DEFAULT_SCENE_SIZE
    ) -> tuple[int, int]:
        """
        Get the position tuple (x, y) of this position according
        to the scene defined by the provided 'scene_size'. That
        position belongs to a coordinate in which you can place
        the center of any element.

        This works considering the upper left corner as the (0, 0)
        coordinate.
        """
        scene_size = (
            DEFAULT_SCENE_SIZE
            if scene_size is None else
            scene_size
        )
        validate_size(scene_size, 'scene_size')

        # Alias to simplify :)
        w, h = scene_size

        return {
            Position.RANDOM_INSIDE: lambda: Position.get_random_inside().get_moviepy_center_tuple(),
            Position.RANDOM_OUTSIDE: lambda: Position.get_random_outside().get_moviepy_center_tuple(),
            Position.CENTER: lambda: (w / 2, h / 2),
            Position.IN_EDGE_TOP: lambda: (w / 2, 0),
            Position.IN_EDGE_BOTTOM: lambda: (w / 2, h),
            Position.IN_EDGE_LEFT: lambda: (0, h / 2),
            Position.IN_EDGE_RIGHT: lambda: (w, h / 2),
            Position.IN_EDGE_TOP_LEFT: lambda: (0, 0),
            Position.IN_EDGE_TOP_RIGHT: lambda: (w, 0),
            Position.IN_EDGE_BOTTOM_RIGHT: lambda: (w, h),
            Position.IN_EDGE_BOTTOM_LEFT: lambda: (0, h),
            Position.HALF_LEFT: lambda: (w / 4, h / 2),
            Position.HALF_TOP_LEFT: lambda: (w / 4, h / 4),
            Position.HALF_TOP: lambda: (w / 2, h / 4),
            Position.HALF_TOP_RIGHT: lambda: (3 * w / 4, h / 4),
            Position.HALF_RIGHT: lambda: (3 * w / 4, h / 2),
            Position.HALF_BOTTOM_RIGHT: lambda: (3 * w / 4, 3 * h / 4),
            Position.HALF_BOTTOM: lambda: (w / 2, 3 * h / 4),
            Position.HALF_BOTTOM_LEFT: lambda: (w / 4, 3 * h / 4),
            Position.OUT_LEFT: lambda: (-w, h / 2),
            Position.OUT_TOP: lambda: (w / 2, -h / 2),
            Position.OUT_RIGHT: lambda: (w + w / 2, h / 2),
            Position.OUT_BOTTOM: lambda: (w / 2, h + h / 2),
            Position.OUT_TOP_LEFT: lambda: (-w, -h / 2),
            Position.OUT_TOP_RIGHT: lambda: (w + w / 2, -h / 2),
            Position.OUT_BOTTOM_LEFT: lambda: (-w, h + h / 2),
            Position.OUT_BOTTOM_RIGHT: lambda: (w + w / 2, h + h / 2)
        }[self]()
    
    def get_moviepy_upper_left_corner_tuple(
        self,
        video_size: tuple,
        scene_size: tuple = DEFAULT_SCENE_SIZE
    ) -> tuple[int, int]:
        """
        Get the position tuple (x, y) of this position according
        to the scene defined by the provided 'scene_size'. That 
        position belongs to a coordinate in which we need to put
        the moviepy video upper left corner to make its center be
        placed in this position.

        This method is useful to position a video in this desired
        position as it returns the value that can be directly used
        in 'with_position' method.

        This works considering the upper left corner as the (0, 0)
        coordinate.
        """
        validate_size(video_size, 'video_size')
        
        # Obtain the position in which the center of the video
        # must be placed
        center_position = self.get_moviepy_center_tuple(scene_size)
        # TODO: Maybe force integer value (?)

        # Obtain the position in which we should place the video
        # (the upper left corner) to make the center of the video
        # be on that 'position_in_scene' position
        upper_left_corner = (center_position[0] - video_size[0] / 2, center_position[1] - video_size[1] / 2)

        return upper_left_corner
    
    def get_manim_position_center(
        self
    ) -> tuple[float, float]:
        """
        Get the position tuple (x, y, z) of this position according
        to the manim scene. That position belongs to a coordinate
        in which we need to put the manim video center to make its
        center be placed in this position.

        The 'z' value is always 0 as this is for a 2D scene.

        This works considering the upper left corner as the 
        (-HALF_MANIM_SCENE_WIDTH, -HALF_MANIM_SCENE_HEIGHT) 
        coordinate.
        """
        # Alias to simplify :)
        hw, hh = DEFAULT_MANIM_SCENE_SIZE[0] / 2, DEFAULT_MANIM_SCENE_SIZE[1] / 2

        return {
            Position.RANDOM_INSIDE: lambda: Position.get_random_inside().get_manim_position_center(),
            Position.RANDOM_OUTSIDE: lambda: Position.get_random_outside().get_manim_position_center(),
            Position.CENTER: lambda: (0, 0, 0),
            Position.IN_EDGE_TOP: lambda: (0, hh, 0),
            Position.IN_EDGE_BOTTOM: lambda: (0, -hh, 0),
            Position.IN_EDGE_LEFT: lambda: (-hw, 0, 0),
            Position.IN_EDGE_RIGHT: lambda: (hw, 0, 0),
            Position.IN_EDGE_TOP_LEFT: lambda: (-hw, hh, 0),
            Position.IN_EDGE_TOP_RIGHT: lambda: (hw, hh, 0),
            Position.IN_EDGE_BOTTOM_RIGHT: lambda: (hw, -hh, 0),
            Position.IN_EDGE_BOTTOM_LEFT: lambda: (-hw, -hh, 0),
            Position.HALF_LEFT: lambda: (-hw / 2, 0, 0),
            Position.HALF_TOP_LEFT: lambda: (-hw / 2, hh / 2, 0),
            Position.HALF_TOP: lambda: (0, hh / 2, 0),
            Position.HALF_TOP_RIGHT: lambda: (hw / 2, hh / 2, 0),
            Position.HALF_RIGHT: lambda: (hw / 2, 0, 0),
            Position.HALF_BOTTOM_RIGHT: lambda: (hw / 2, -hh / 2, 0),
            Position.HALF_BOTTOM: lambda: (0, -hh / 2, 0),
            Position.HALF_BOTTOM_LEFT: lambda: (-hw / 2, -hh / 2, 0),
            Position.OUT_LEFT: lambda: (2 * -hw, 0, 0),
            Position.OUT_TOP: lambda: (0, 2 * hh, 0),
            Position.OUT_RIGHT: lambda: (2 * hw, 0, 0),
            Position.OUT_BOTTOM: lambda: (0, 2 * -hh, 0),
            Position.OUT_TOP_LEFT: lambda: (2 * -hw, 2 * hh),
            Position.OUT_TOP_RIGHT: lambda: (2 * hw, 2 * hh),
            Position.OUT_BOTTOM_LEFT: lambda: (2 * -hw, 2 * -hh),
            Position.OUT_BOTTOM_RIGHT: lambda: (2 * hw, 2 * -hh)
        }[self]()

    @staticmethod
    def to_coordinate(
        position: 'Position'
    ) -> 'Coordinate':
        """
        Turn the provided 'position' (that must be a tuple of
        2 elements) a coordinate.
        """
        position = Position.to_enum(position)

        position = position.get_moviepy_center_tuple()

        # TODO: If we return the tuple only and we say that you
        # can instantiate the Coordinate class in the library 
        # that uses this method, you can avoid the dependency
        # here.
        #return position[0], position[1]
        return Coordinate(position[0], position[1])
    
    # We don't need any upper left for manim because it
    # uses the center of the elements to position them
    
class DependantPosition(Enum):
    """
    Enum class that represents different positions within a
    scene of 1920x1080 that need a calculation because it
    depends on the size of the element we are trying to 
    position.
    """

    # TODO: Avoid the ones in Position that should not
    # be replaced
    TOP = 'top'
    TOP_RIGHT = 'top_right'
    RIGHT = 'right'
    BOTTOM_RIGHT = 'bottom_right'
    BOTTOM = 'bottom'
    BOTTOM_LEFT = 'bottom_left'
    LEFT = 'left'
    TOP_LEFT = 'top_left'

    OUT_TOP = 'out_top'
    OUT_TOP_RIGHT = 'out_top_right'
    OUT_RIGHT = 'out_right'
    OUT_BOTTOM_RIGHT = 'out_bottom_right'
    OUT_BOTTOM = 'out_bottom'
    OUT_BOTTOM_LEFT = 'out_bottom_left'
    OUT_LEFT = 'out_left'
    OUT_TOP_LEFT = 'out_top_left'

    QUADRANT_1_TOP_RIGHT_CORNER = 'quadrant_1_top_right_corner'
    QUADRANT_1_BOTTOM_RIGHT_CORNER = 'quadrant_1_bottom_right_corner'
    QUADRANT_1_BOTTOM_LEFT_CORNER = 'quadrant_1_bottom_left_corner'
    QUADRANT_2_TOP_LEFT_CORNER = 'quadrant_2_top_left_corner'
    QUADRANT_2_BOTTOM_RIGHT_CORNER = 'quadrant_2_bottom_right_corner'
    QUADRANT_2_BOTTOM_LEFT_CORNER = 'quadrant_2_bottom_left_corner'
    QUADRANT_3_TOP_RIGHT_CORNER = 'quadrant_3_top_right_corner'
    QUADRANT_3_TOP_LEFT_CORNER = 'quadrant_3_top_left_corner'
    QUADRANT_3_BOTTOM_LEFT_CORNER = 'quadrant_3_bottom_left_corner'
    QUADRANT_4_TOP_RIGHT_CORNER = 'quadrant_4_top_right_corner'
    QUADRANT_4_TOP_LEFT_CORNER = 'quadrant_4_top_left_corner'
    QUADRANT_4_BOTTOM_RIGHT_CORNER = 'quadrant_4_bottom_right_corner'

    RANDOM_INSIDE = 'random_inside'
    RANDOM_OUTSIDE = 'random_outside'

    @staticmethod
    def _get_outside_items_as_list(
    ) -> list['DependantPosition']:
        """
        Get a list of the DependantPosition items that are placed
        outside of the screen limits.
        """
        return [
            DependantPosition.OUT_TOP_LEFT,
            DependantPosition.OUT_TOP,
            DependantPosition.OUT_RIGHT,
            DependantPosition.OUT_BOTTOM_RIGHT,
            DependantPosition.OUT_BOTTOM,
            DependantPosition.OUT_BOTTOM_LEFT,
            DependantPosition.OUT_LEFT
        ]
    
    @staticmethod
    def _get_inside_items_as_list(
    ) -> list['DependantPosition']:
        """
        Get a list of the DependantPosition items that are placed
        inside of the screen limits.
        """
        return [
            DependantPosition.TOP,
            DependantPosition.TOP_RIGHT,
            DependantPosition.RIGHT,
            DependantPosition.BOTTOM_RIGHT,
            DependantPosition.BOTTOM,
            DependantPosition.BOTTOM_LEFT,
            DependantPosition.LEFT,
            DependantPosition.TOP_LEFT,
            DependantPosition.QUADRANT_1_TOP_RIGHT_CORNER,
            DependantPosition.QUADRANT_1_BOTTOM_RIGHT_CORNER,
            DependantPosition.QUADRANT_1_BOTTOM_LEFT_CORNER,
            DependantPosition.QUADRANT_2_TOP_LEFT_CORNER,
            DependantPosition.QUADRANT_2_BOTTOM_RIGHT_CORNER,
            DependantPosition.QUADRANT_2_BOTTOM_LEFT_CORNER,
            DependantPosition.QUADRANT_3_TOP_RIGHT_CORNER,
            DependantPosition.QUADRANT_3_TOP_LEFT_CORNER,
            DependantPosition.QUADRANT_3_BOTTOM_LEFT_CORNER,
            DependantPosition.QUADRANT_4_TOP_RIGHT_CORNER,
            DependantPosition.QUADRANT_4_TOP_LEFT_CORNER,
            DependantPosition.QUADRANT_4_BOTTOM_RIGHT_CORNER
        ]

        # This below is not working, so I put it
        # manually by now...
        return [
            dependant_position
            for dependant_position in DependantPosition.get_all()
            if dependant_position not in [
                *DependantPosition._get_outside_items_as_list(),
                DependantPosition.RANDOM_INSIDE,
                DependantPosition.RANDOM_OUTSIDE
            ]
        ]
    
    @staticmethod
    def get_random_outside(
    ) -> 'DependantPosition':
        """
        Get one random DependantPosition element that is placed
        outside of the screen limits.
        """
        return randchoice(DependantPosition._get_outside_items_as_list())
    
    @staticmethod
    def get_random_inside(
    ) -> 'DependantPosition':
        """
        Get one random DependantPosition element that is placed
        inside of the screen limits.
        """
        return randchoice(DependantPosition._get_inside_items_as_list())

    def get_moviepy_position_center(
        self,
        video_size: tuple = DEFAULT_SCENE_SIZE,
        scene_size: tuple = DEFAULT_SCENE_SIZE
    ) -> tuple[int, int]:
        """
        Get the position tuple (x, y) of this position according
        to the scene defined by the provided 'scene_size'. That 
        position belongs to a coordinate in which we need to put
        the moviepy video center to be placed in the desired
        position.

        This method is useful cannot be used directly to position
        a video as it is returning the coordinate in which the
        center must be placed and moviepy uses the upper left
        corner to be positioned, so consider using the method
        'get_moviepy_position_upper_left_corner' to obtain it.

        This works considering the upper left corner of the scene
        as the (0, 0) coordinate.
        """
        video_size = (
            DEFAULT_SCENE_SIZE
            if video_size is None else
            video_size
        )
        validate_size(video_size, 'video_size')

        scene_size = (
            DEFAULT_SCENE_SIZE
            if scene_size is None else
            scene_size
        )
        validate_size(scene_size, 'scene_size')
            
        # Alias to simplify :)
        sw, sh = scene_size
        vw, vh = video_size

        # TODO: Maybe rename to be like in Position 
        return {
            DependantPosition.RANDOM_INSIDE: lambda: DependantPosition.get_random_inside().get_moviepy_position_center(),
            DependantPosition.RANDOM_OUTSIDE: lambda: DependantPosition.get_random_outside().get_moviepy_position_center(),
            DependantPosition.TOP: lambda: (sw / 2, -vh / 2),
            DependantPosition.RIGHT: lambda: (sw - vw / 2, sh / 2),
            DependantPosition.BOTTOM: lambda: (sw / 2, sh - vh),
            DependantPosition.LEFT: lambda: (vw / 2, sh / 2),
            DependantPosition.TOP_RIGHT: lambda: (sw - vw / 2, vh / 2),
            DependantPosition.BOTTOM_RIGHT: lambda: (sw - vw / 2, sh - vh / 2),
            DependantPosition.BOTTOM_LEFT: lambda: (vw / 2, sh - vh / 2),
            DependantPosition.TOP_LEFT: lambda: (vw / 2, vh / 2),
            DependantPosition.OUT_TOP: lambda: (sw / 2, -vh / 2),
            DependantPosition.OUT_TOP_RIGHT: lambda: (sw + vw / 2, -vh / 2),
            DependantPosition.OUT_RIGHT: lambda: (sw + vw / 2, sh / 2),
            DependantPosition.OUT_BOTTOM_RIGHT: lambda: (sw + vw / 2, sh + vh / 2),
            DependantPosition.OUT_BOTTOM: lambda: (sw / 2, sh + vh / 2),
            DependantPosition.OUT_BOTTOM_LEFT: lambda: (-vw / 2, sh + vh / 2),
            DependantPosition.OUT_LEFT: lambda: (-vw / 2, sh / 2),
            DependantPosition.OUT_TOP_LEFT: lambda: (-vw / 2, -vh / 2),
            DependantPosition.QUADRANT_1_TOP_RIGHT_CORNER: lambda: (sw / 2 - vw / 2, vh / 2),
            DependantPosition.QUADRANT_1_BOTTOM_RIGHT_CORNER: lambda: (sw / 2 - vw / 2, sh / 2 - vh / 2),
            DependantPosition.QUADRANT_1_BOTTOM_LEFT_CORNER: lambda: (vw / 2, sh / 2 - vh / 2),
            DependantPosition.QUADRANT_2_TOP_LEFT_CORNER: lambda: (sw / 2 + vw / 2, vh / 2),
            DependantPosition.QUADRANT_2_BOTTOM_RIGHT_CORNER: lambda: (sw - vw / 2, sh / 2 - vh / 2),
            DependantPosition.QUADRANT_2_BOTTOM_LEFT_CORNER: lambda: (sw / 2 + vw / 2, sh / 2 - vh / 2),
            DependantPosition.QUADRANT_3_TOP_RIGHT_CORNER: lambda: (sw - vw / 2, sh / 2 + vh / 2),
            DependantPosition.QUADRANT_3_TOP_LEFT_CORNER: lambda: (sw / 2 + vw / 2, sh / 2 + vh / 2),
            DependantPosition.QUADRANT_3_BOTTOM_LEFT_CORNER: lambda: (sw / 2 + vw / 2, sh - vh / 2),
            DependantPosition.QUADRANT_4_TOP_RIGHT_CORNER: lambda: (sw / 2 - vw / 2, sh / 2 + vh / 2),
            DependantPosition.QUADRANT_4_TOP_LEFT_CORNER: lambda: (vw / 2, sh / 2 + vh / 2),
            DependantPosition.QUADRANT_4_BOTTOM_RIGHT_CORNER: lambda: (sw / 2 - vw / 2, sh - vh / 2)
        }[self]()

    # TODO: Rename as in Position
    def get_moviepy_position_upper_left_corner(
        self,
        video_size: tuple,
        scene_size: tuple = DEFAULT_SCENE_SIZE
    ) -> tuple[int, int]:
        """
        Get the position tuple (x, y) of this position according
        to the scene defined by the provided 'scene_size'. That 
        position belongs to a coordinate in which we need to put
        the moviepy video upper left corner to make its center be
        placed in this position.

        This method is useful to position a video in this desired
        position as it returns the value that can be directly used
        in 'with_position' method.

        This works considering the upper left corner as the (0, 0)
        coordinate.
        """
        # Obtain the position in which the center of the video
        # must be placed
        center_position = self.get_moviepy_position_center(video_size, scene_size)
        # TODO: Maybe force integer value (?)

        # Obtain the position in which we should place the video
        # (the upper left corner) to make the center of the video
        # be on that previously obtained 'center_position' position
        upper_left_corner = (center_position[0] - video_size[0] / 2, center_position[1] - video_size[1] / 2)

        return upper_left_corner

    def get_manim_position_center(
        self,
        video_size: tuple
    ) -> tuple[float, float]:
        if video_size is None:
            raise Exception('No "video_size" provided.')
        
        validate_size(video_size, 'video_size')
        
        # Alias to simplify :)
        hsw, hsh = DEFAULT_MANIM_SCENE_SIZE[0] / 2, DEFAULT_MANIM_SCENE_SIZE[1] / 2
        vw, vh = video_size

        return {
            DependantPosition.TOP: lambda: (0, hsh - vh / 2, 0),
            DependantPosition.TOP_RIGHT: lambda: (hsw - vw / 2, hsh - vh / 2, 0),
            DependantPosition.RIGHT: lambda: (hsw - vw / 2, 0, 0),
            DependantPosition.BOTTOM_RIGHT: lambda: (hsw - vw / 2, -hsh + vh / 2, 0),
            DependantPosition.BOTTOM: lambda: (0, -hsh + vh / 2, 0),
            DependantPosition.BOTTOM_LEFT: lambda: (-hsw + vw / 2, -hsh + vh / 2, 0),
            DependantPosition.LEFT: lambda: (-hsw + vw / 2, 0, 0),
            DependantPosition.TOP_LEFT: lambda: (-hsw + vw / 2, hsh - vh / 2, 0),
            DependantPosition.OUT_TOP_LEFT: lambda: (-hsw - vw / 2, hsh + vh / 2, 0),
            DependantPosition.OUT_TOP: lambda: (0, hsh + vh / 2, 0),
            DependantPosition.OUT_TOP_RIGHT: lambda: (hsw + vw / 2, hsh + vh / 2, 0),
            DependantPosition.OUT_RIGHT: lambda: (hsw + vw / 2, 0, 0),
            DependantPosition.OUT_BOTTOM_RIGHT: lambda: (hsw + vw / 2, -hsh - vh / 2, 0),
            DependantPosition.OUT_BOTTOM: lambda: (0, -hsh - vh / 2, 0),
            DependantPosition.OUT_BOTTOM_LEFT: lambda: (-hsw - vw / 2, -hsh - vh / 2, 0),
            DependantPosition.OUT_LEFT: lambda: (-hsw - vh / 2, 0, 0),
            DependantPosition.QUADRANT_1_TOP_RIGHT_CORNER: lambda: (-vw / 2, hsh - vh / 2, 0),
            DependantPosition.QUADRANT_1_BOTTOM_RIGHT_CORNER: lambda: (-vw / 2, vh / 2, 0),
            DependantPosition.QUADRANT_1_BOTTOM_LEFT_CORNER: lambda: (-hsw + vw / 2, vh / 2, 0),
            DependantPosition.QUADRANT_2_TOP_LEFT_CORNER: lambda: (vw / 2, hsh - vh / 2, 0),
            DependantPosition.QUADRANT_2_BOTTOM_RIGHT_CORNER: lambda: (hsw - vw / 2, vh / 2, 0),
            DependantPosition.QUADRANT_2_BOTTOM_LEFT_CORNER: lambda: (vw / 2, vh / 2, 0),
            DependantPosition.QUADRANT_3_TOP_LEFT_CORNER: lambda: (vw / 2, -vh / 2, 0),
            DependantPosition.QUADRANT_3_TOP_RIGHT_CORNER: lambda: (hsw - vw / 2, -vh / 2, 0),
            DependantPosition.QUADRANT_3_BOTTOM_LEFT_CORNER: lambda: (vw / 2, -hsh + vh / 2, 0),
            DependantPosition.QUADRANT_4_TOP_LEFT_CORNER: lambda: (-hsw + vw / 2, -vh / 2, 0),
            DependantPosition.QUADRANT_4_TOP_RIGHT_CORNER: lambda: (-vw / 2, -vh / 2, 0),
            DependantPosition.QUADRANT_4_BOTTOM_RIGHT_CORNER: lambda: (-vw / 2, -hsh + vh / 2, 0),
            DependantPosition.RANDOM_INSIDE: lambda: DependantPosition.get_random_inside().get_manim_position_center((vw, vh)),
            DependantPosition.RANDOM_OUTSIDE: lambda: DependantPosition.get_random_outside().get_manim_position_center((vw, vh))
        }[self]()
    

 