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


# TODO: This class is for testing, but if
# definitive, it must me moved to another
# module
class ManimAnimationOnTimeline:
    """
    Class to wrap the information about an animation
    that will be set in a timeline to handle when it
    must be played.
    """

    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the animation.
        """
        return self.t_end - self.t_start

    def __init__(
        self,
        t_start: float,
        t_end: float,
        animation: any
    ):
        # TODO: Validate
        self.t_start = t_start
        self.t_end = t_end
        self.animation = animation

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
        square = Square().shift(LEFT * 2)
        circle = Circle().shift(RIGHT * 2)

        self.add(square, circle)

        square.generate_target()
        square.target.shift(RIGHT * 4)

        circle.generate_target()
        circle.target.scale(1.5)

        animation_one = ManimAnimationOnTimeline(1, 3, MoveToTarget(square))
        animation_two = ManimAnimationOnTimeline(2, 4, MoveToTarget(circle))

        animations_on_timeline = [
            animation_one,
            animation_two
        ]

        timeline_end_time = max(
            animation_on_timeline.t_end
            for animation_on_timeline in animations_on_timeline
        )
        
        animations = []
        for animation_on_timeline in animations_on_timeline:
            self.compile_animations
            full_animation = Succession(
                Wait(animation_on_timeline.t_start),
                animation_on_timeline.animation.set_run_time(animation_on_timeline.duration),
                Wait(timeline_end_time - animation_on_timeline.t_end),
            )
            animations.append(full_animation)

        self.play(AnimationGroup(*animations, lag_ratio = 0))