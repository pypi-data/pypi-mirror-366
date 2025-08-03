from yta_validation.parameter import ParameterValidator
from manim import Wait, Succession, Scene, AnimationGroup


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
        ParameterValidator.validate_mandatory_positive_number('t_start', t_start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('t_end', t_end, do_include_zero = False)

        self.t_start: float = t_start
        """
        The time moment (in seconds) in which the animation
        must start being played.
        """
        self.t_end: float = t_end
        """
        The time moment (in seconds) in which the animation
        must stop being played.
        """
        self.animation = animation

class ManimTimeline:
    """
    Class to represent the timeline of a whole
    animation in Manim, able to store different
    mobjects and animations on it with their
    time moments and peculiarities.
    """

    @property
    def t_end(
        self
    ) -> float:
        """
        The time moment (in seconds) in which the last
        animation of the timeline must stop being played.
        """
        return max(
            animation.t_end
            for animation in self.animations
        )
    
    @property
    def compiled_animations(
        self
    ) -> list[Succession]:
        """
        A list of Succession instances that are the
        different animations prepared to be played
        with the next code in a Scene instance:
        
        - `self.play(AnimationGroup(*compiled_animations, lag_ratio = 0))`
        """
        return [
            Succession(
                Wait(anim.t_start),
                anim.animation.set_run_time(anim.duration),
                Wait(self.t_end - anim.t_end),
            )
            for anim in self.animations
        ]

    def __init__(
        self
    ):
        self.animations: list[ManimAnimationOnTimeline] = []
        """
        The raw animations, as they were stored, that
        we want to play.
        """

    def add_animation(
        self,
        animation: ManimAnimationOnTimeline
    ) -> 'ManimTimeline':
        """
        Add the provided 'animation' to the internal
        list of animations that must be displayed.

        This is an example of a valid animation we 
        can create to pass here as parameter:

        - `circle = Circle().shift(RIGHT * 2)`
        - `circle.generate_target()`
        - `circle.target.scale(1.5)`
        - `animation_two = ManimAnimationOnTimeline(2, 6, MoveToTarget(circle))`
        """
        ParameterValidator.validate_mandatory_instance_of('animation', animation, ManimAnimationOnTimeline)

        self.animations.append(animation)

        return self

    def play(
        self,
        scene: Scene
    ):
        """
        Make the provided 'scene' play the animations we
        have stored in this instance.
        """
        scene.play(AnimationGroup(*self.compiled_animations, lag_ratio = 0))
    
def _test_animation(
) -> any:
    """
    *For internal use only.*

    A valid animation we can use in the ManimTimeline 
    '.add_animation()' method to test that is working
    properly.
    """
    from manim import Circle, RIGHT, MoveToTarget

    circle = Circle().shift(RIGHT * 2)
    circle.generate_target()
    circle.target.scale(1.5)
    return ManimAnimationOnTimeline(2, 6, MoveToTarget(circle))