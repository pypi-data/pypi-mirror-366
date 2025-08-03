"""
The dimensions in the Manim scene are different
than the ones in moviepy, thats why we need to
use them properly and transform.

Manim dimensions system is (14 + 2/9)w x (8)h,
which means that the width is 14 + 2/9 and the
height is 8. The upper left corner coordinate is
[-7-1/9, 4, 0] (0 is the z axis), and the lower
right corner coordinate is [7+1/9, -4, 0],
because the center of the scene and screen is
the origin [0, 0, 0].
"""
from yta_constants.multimedia import DEFAULT_MANIM_SCENE_SIZE, DEFAULT_SCENE_SIZE
from manim import *


class ManimDimensions:
    """
    Class to encapsulate and simplify the functionality related to manim
    dimensions. Manim works with specific dimensions that are not measured
    in pixels and we use to work with pixels. This class was created to
    let us work with pixel dimensions that will be translated into manim
    dimensions to simplify the creative process.

    We consider that a manim screen has 1920x1080 dimensions in pixels, so
    those are the pixel dimensions you should keep in mind for your
    calculations.

    Manim dimensions system is (14 + 2/9)w x (8)h, which means that the 
    width is 14 + 2/9 and the height is 8. The upper left corner coordinate
    is [-7-1/9, 4, 0] (0 is the z axis), and the lower right corner 
    coordinate is [7+1/9, -4, 0], because the center of the scene and screen
    is the origin [0, 0, 0].
    """

    @staticmethod
    def width_to_manim_width(
        width: float
    ) -> float:
        """
        Turns the pixel 'width' provided dimension to the corresponding manim
        width dimension. Remember that the system is prepared to work with a
        simulated screen of 1920x1080 pixels, so providing a 'width' of 1920
        will make the object fit the whole manim screen width.
        """
        return (width * DEFAULT_MANIM_SCENE_SIZE[0]) / DEFAULT_SCENE_SIZE[0]
    
    @staticmethod
    def manim_width_to_width(
        manim_width: float
    ) -> float:
        """
        Turns the provided 'manim_width' dimension to the corresponding pixel
        width dimension based on our simulated screen size of 1920x1080 pixels.
        That means that providing a 'manim_width' of 14 + 2/9 will return 1920
        as pixel width, that is the screen size for our simulated whole screen.
        """
        # TODO: Maybe check if 'manim_width' is too big to raise
        # an exception or, at least, print a message
        return (manim_width * DEFAULT_SCENE_SIZE[0]) / DEFAULT_MANIM_SCENE_SIZE[0]
    
    @staticmethod
    def height_to_manim_height(
        height: float
    ) -> float:
        """
        Turns the pixel 'height' provided dimension to the corresponding manim
        height dimension. Remember that the system is prepared to work with a
        simulated screen of 1920x1080 pixels, so providing a 'height' of 1080
        will make the object fit the whole manim screen height.
        """
        return (height * DEFAULT_MANIM_SCENE_SIZE[1]) / DEFAULT_SCENE_SIZE[1]
    
    @staticmethod
    def manim_height_to_height(
        manim_height: float
    ) -> float:
        """
        Turns the provided 'manim_height' dimension to the corresponding pixel
        height dimension based on our simulated screen size of 1920x1080 pixels.
        That means that providing a 'manim_height' of 8 will return 1080 as
        pixel height, that is the screen size for our simulated whole screen.
        """
        # TODO: Maybe check if 'manim_height' is too big to raise
        # an exception or, at least, print a message
        return (manim_height * DEFAULT_SCENE_SIZE[1]) / DEFAULT_MANIM_SCENE_SIZE[1]



# TODO: Rename this
class ManimXGenerator:
    """
    Class to simplify and encapsulate the mobject generation functionality.
    """

    @staticmethod
    def mobject_fitting_width(
        mobject: Mobject,
        width: float,
        **kwargs
    ):
        """
        Creates the provided 'mobject' with a size that fits the provided
        'width'. This will be limited to the height. If the new mobject
        height is greater than the screen max height, it will be limited
        to the height.

        If you want a mobject that just fits the provided 'width' ignoring
        the height, just use 'mobject.scale_to_fit_width(width)' instead.
        """
        width = ManimDimensions.width_to_manim_width(width)

        # We build both width and height fitted and get the most limited
        mobject_width_fitted = mobject(**kwargs).scale_to_fit_width(width)
        mobject_height_fitted = mobject(**kwargs).scale_to_fit_height(width)

        # As it is a 16:9 proportion, the height is the measure that limits the most
        return (
            mobject_height_fitted
            if mobject_height_fitted.width < mobject_width_fitted.width else
            mobject_width_fitted
        )
    
    def mobject_fitting_height(
        mobject: Mobject,
        height: float,
        **kwargs
    ):
        """
        Creates the provided 'mobject' with a size that fits the provided
        'height'. This will be limited to the width. If the new mobject
        width is greater than the screen max width, it will be limited
        to the width.

        If you want a mobject that just fits the provided 'height' ignoring
        the width, just use 'mobject.scale_to_fit_height(height)' instead.
        """
        height = ManimDimensions.height_to_manim_height(height)

        # We build both width and height fitted and get the most limited
        mobject_height_fitted = mobject(**kwargs).scale_to_fit_height(height)
        mobject_width_fitted = mobject(**kwargs).scale_to_fit_width(height)

        # As it is a 16:9 proportion, the height is the measure that limits the most
        # TODO: When it was Text the mobject I used the font.size to compare
        return (
            mobject_height_fitted
            if mobject_height_fitted.width < mobject_width_fitted.width else
            mobject_width_fitted
        )
        # Another option:
        return min(mobject_height_fitted, mobject_width_fitted, key = lambda el: el.width)
    
    def mobject_fitting_fullscreen(
        mobject: Mobject,
        **kwargs
    ):
        """
        Creates the provided 'mobject' with a size to fit the whole screen.
        This method will return the provided 'mobject' fitting the standard
        whole screen. The mobject will be cropped if its aspect ratio is not 
        16:9, but it will fit the whole screen for sure.
        """
        image_width_fitted = mobject(**kwargs).scale_to_fit_width(ManimDimensions.width_to_manim_width(DEFAULT_SCENE_SIZE[0]))

        # We want the mobject that occupies the whole screen
        if ManimDimensions.manim_height_to_height(image_width_fitted.height) >= DEFAULT_SCENE_SIZE[1]:
            return image_width_fitted
        
        image_height_fitted = mobject(**kwargs).scale_to_fit_height(ManimDimensions.height_to_manim_height(DEFAULT_SCENE_SIZE[1]))

        return image_height_fitted
    
    def mobject_fitting_screen(
        mobject: Mobject,
        **kwargs
    ):
        """
        Scales the provided 'mobject' if necessary to fit the screen. That 
        means that a mobject bigger than the screen size will be cropped
        to fit inside. One of the two dimensions (width or height) could
        be out of bounds if the provided 'mobject' is bigger than the 
        screen size when provided.
        """
        mobject = mobject(**kwargs)

        mobject = (
            mobject.scale_to_fit_width(ManimDimensions.width_to_manim_width(DEFAULT_SCENE_SIZE[0]))
            if ManimDimensions.manim_width_to_width(mobject.width) > DEFAULT_SCENE_SIZE[0] else
            mobject.scale_to_fit_height(ManimDimensions.height_to_manim_height(DEFAULT_SCENE_SIZE[1]))
            if ManimDimensions.manim_height_to_height(mobject.height) > DEFAULT_SCENE_SIZE[1] else
            mobject
        )

    # TODO: Maybe we don't have to instantiate the mobject but resizing
    # it so 'mobject(**kwargs)' is not the way.


# TODO: You can do this below so you don't need to declare all args
# just pass the **kwargs and let the user build the 'color', 
# 'font_size' and all params he wants.
"""
kwargs = {
    'color': BLUE,
    'font_size': 22
}
self.play(Text('hola', **kwargs).animate.rotate(90 * DEGREES), run_time = 2)
"""
