"""
This module is about my own Animations, that
inherit from the ones from Manim, but its 
not about a complex animation that I can 
render but a new animation I created to make
easier creating complex animations.

TODO: Refactor this project structure 
because this 'animations' module is confusing
according to the different type of animations
we have (the ones from Manim, the simple ones
I created, and the complex ones to render as
a 'final product').
"""
from yta_video_manim.settings import INSTANTANEOUS_RUN_TIME
from manim import *


class MoveInstantlyTo(Succession):
    """
    The element will be moved in one frame and
    then will be waiting statically the rest of
    the time defined by the 'run_time'.
    """

    def __init__(
        self,
        mobject: Mobject,
        # TODO: Accept 'Position' instances (?)
        position: tuple[float, float, float] = [2, 1, 0],
        run_time: float = 1
    ):
        # TODO: Validate 'position' (?)
        super().__init__(
            # Move instantly
            ApplyMethod(mobject.move_to, position, run_time = INSTANTANEOUS_RUN_TIME),
            # Wait the rest of the time
            Wait(run_time - INSTANTANEOUS_RUN_TIME),
        )

class MakeDissapearInstantly(Succession):
    """
    Move the Mobject instantly out of the scene so
    it becames invisible but still placed on it.
    """

    def __init__(
        self,
        mobject: Mobject
    ):
        super().__init__(
            MoveInstantlyTo(mobject, [-20, -20, 0], run_time = INSTANTANEOUS_RUN_TIME)
        )

class MakeAppearInstantly(Succession):

    def __init__(
        self,
        mobject: Mobject,
        position: tuple[float, float, float] = [2, 1, 0]
    ):
        super().__init__(
            MoveInstantlyTo(mobject, position, run_time = INSTANTANEOUS_RUN_TIME)
        )