from yta_video_manim.dimensions import ManimDimensions
from yta_validation.parameter import ParameterValidator


class LoadingBarImage:

    def __init__(
        self,
        image_filename: str,
        y: int,
        start_percentage: int,
        end_percentage: int
    ):
        """
        An object that represents an image that will be used in the loading
        bar to improve the animation quality. This image will be static or
        dynamic. If 'start_percentage' and 'end_percentage' are the same,
        the image will be static at that percentage point. If not, it will
        move from 'start_percentage' to 'end_percentage'.

        The 'y' parameter is the vertical distance from the loading bar. 
        This is useful to position the image above, below or inside the
        bar.
        """
        ParameterValidator.validate_mandatory_string('image_filename', image_filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_number_between('start_percentage', start_percentage, 0, 100)
        ParameterValidator.validate_mandatory_number_between('end_percentage', end_percentage, 0, 100)
        ParameterValidator.validate_mandatory_number_between('y', y, -100, 100)
        
        self.image_filename = image_filename
        self.start_percentage = start_percentage
        self.end_percentage = end_percentage
        self.y = ManimDimensions.height_to_manim_height(y)
        # This is for the right movement
        self.start_x = 0
        self.end_x = 0

    def toJSON(self):
        return {
            'image_filename': self.image_filename,
            'y': self.y,
            'start_percentage': self.start_percentage,
            'end_percentage': self.end_percentage
        }