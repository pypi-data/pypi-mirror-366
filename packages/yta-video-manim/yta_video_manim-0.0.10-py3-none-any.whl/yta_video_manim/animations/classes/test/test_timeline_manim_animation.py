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
        from yta_video_manim.animations.custom import MoveInstantlyTo

        timeline = ManimTimeline()
        
        square = Square().set_color(RED).shift(LEFT * 2)
        circle = Circle().set_color(BLUE).shift(RIGHT * 2)
        self.add(square, circle)

        timeline.add_animation(ManimAnimationOnTimeline(0, 1, FadeIn(square).set_run_time(1)))
        timeline.add_animation(ManimAnimationOnTimeline(1, 3, Succession(Wait(0), MoveInstantlyTo(square))))
        timeline.add_animation(ManimAnimationOnTimeline(3, 4, Succession(Wait(0), ApplyFunction(lambda m: m.move_to([-2, -1, 0]), square, run_time=1e-6))))
        timeline.add_animation(ManimAnimationOnTimeline(4, 5, FadeOut(square).set_run_time(1)))

        timeline.play(self)



        return
        self.play(AnimationGroup(*timeline.compiled_animations, lag_ratio = 0))

        # Animación 1: cuadrado desde t=0 a t=1
        square_anim = Succession(
            square.animate.shift(UP * 2).set_run_time(1),
            ApplyFunction(lambda m: self.remove(m), square, run_time= 1/60)
        )

        # Animación 2: círculo desde t=1 a t=3
        circle_anim = Succession(
            Wait(1),  # delay de 1s
            circle.animate.scale(2).set_run_time(2)
        )

        # Agrupar ambas
        self.play(
            AnimationGroup(
                square_anim,
                circle_anim,
                lag_ratio=0  # ambas se gestionan desde el mismo punto de tiempo global
            )
        )

        # animation_three = ManimAnimationOnTimeline(0, 2, animation_three)

        # timeline.add_animation(animation_one).add_animation(animation_two).add_animation(animation_three)
        # self.play(AnimationGroup(*timeline.compiled_animations, lag_ratio = 0))