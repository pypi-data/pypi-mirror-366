"""
This class is to make complex testings.
"""
from yta_video_manim.animations.base_manim_animation import BaseManimAnimation
from yta_video_manim.animations.base_manim_animation_wrapper import BaseManimAnimationWrapper
from yta_constants.manim import ManimRenderer, ManimAnimationType
from yta_programming.output import Output
from yta_constants.file import FileExtension
from manim import *
from typing import Union


class TestTimelineManimAnimationWrapper(BaseManimAnimationWrapper):
    """
    Using a timeline. Just testing.
    """

    __test__ = False

    def __init__(
        self,
    ):
        # TODO: This parameter validation could be done
        # by our specific parameter validator (under
        # construction yet)
        exception_messages = []

        if len(exception_messages) > 0:
            raise Exception('\n'.join([exception_message for exception_message in exception_messages]))
        
        super().__init__(TestTimelineManimAnimationGenerator, ManimAnimationType.GENERAL)

class TestTimelineManimAnimationGenerator(BaseManimAnimation):

    __test__ = False

    def construct(self):
        """
        This method is called by manim when executed by shell and
        will call the scene animation render method to be processed
        and generated.
        """
        self.animate()

    def generate(
        self,
        parameters: dict,
        output_filename: Union[str, None] = None
    ):
        """
        Build the manim animation video and stores it
        locally as the provided 'output_filename', 
        returning the final output filename.

        This method will call the '.animate()' method
        to build the scene with the instructions that
        are written in that method.
        """
        output_filename = Output.get_filename(output_filename, FileExtension.MOV)

        return super().generate(
            parameters,
            renderer = ManimRenderer.CAIRO,
            output_filename = output_filename
        )
    
    def animate(self):
        """
        This code will generate the manim animation and belongs to the
        Scene manim object.
        """
        from yta_video_manim.animations.timeline import ManimTimeline, ManimAnimationOnTimeline
        from yta_constants.multimedia import DEFAULT_SCENE_SIZE
        from yta_video_manim.utils import fitting_text
        from yta_positioning.position import Position

        timeline = ManimTimeline()
        square = Square().shift(LEFT * 2)
        square.generate_target()
        square.target.shift(RIGHT * 4)
        animation_one = ManimAnimationOnTimeline(1, 3, MoveToTarget(square))

        circle = Circle().shift(RIGHT * 2)
        circle.generate_target()
        circle.target.scale(1.5)
        animation_two = ManimAnimationOnTimeline(2, 6, MoveToTarget(circle))

        text = fitting_text('ejemplo', DEFAULT_SCENE_SIZE[0] / 6)
        # TODO: This was previously considering the limits to
        # make the text be always inside the scene, but now...
        #random_coords = Position.RANDOM_INSIDE.get_manim_position_center((text.width, text.height))
        random_coords = Position.RANDOM_INSIDE.get_manim_position_center()
        # text.move_to(random_coords)
        # self.add(text)
        # self.wait(1)
        animation_three = Succession(
            ApplyMethod(text.move_to, random_coords, run_time = 0),
            Wait(1),
        )
        animation_three = ManimAnimationOnTimeline(0, 2, animation_three)

        timeline.add_animation(animation_one).add_animation(animation_two).add_animation(animation_three)
        self.play(AnimationGroup(*timeline.compiled_animations, lag_ratio = 0))