"""
The way we work with manim is special. We have it 
installed and we have to use it through the command
line. Thats why we write the parameters in a file.
The state when we reach the scene creation class is
different than the one in which manim interacts with
that class to build the scene, so we can't keep the
state (and instances). They act separately.

We need to provide the renderer in the generate method
because of the previous condition. We call the class
outside of this state, from manim command calling the
class that creates the scene.
"""
from yta_video_manim.config import ManimConfig
from yta_constants.manim import ManimRenderer
from yta_constants.file import FileExtension
from yta_programming.output import Output
from yta_video_manim.animations.utils import generate_animation
from manim import Scene, config
from abc import abstractmethod
from typing import Union


class BaseManimAnimation(Scene):
    """
    The basic scene class, to be inherited by our own
    classes, to define the animation and the engine to
    render it.
    """

    @abstractmethod
    def animate(
        self
    ):
        """
        The code that creates the manim animation, specific for
        each animation subclass.
        """
        # This must be implemented by the subclass. This is the
        # code that actually generates the video scene by using
        # the manim engine.
        pass

    def setup(
        self
    ):
        """
        This method is called when manim is trying to use it to
        render the scene animation. It is called the first, to
        instantiate it and before the 'construct' method that
        is the one that will render.
        """
        # Preset configuration we need for any scene
        # Disables caching to avoid error when cache is overload
        config.disable_caching = True
        config.max_files_cached = 9999
        # This makes the video background transparent to fit well over the main video
        self.camera.background_opacity = 0.0

        self.parameters = ManimConfig.config

        return self.parameters

    def construct(
        self
    ):
        """
        This method is called by manim when executed by shell and
        will call the scene animation render method to be processed
        and generated.
        """
        self.setup()

    def generate(
        self,
        parameters: dict,
        renderer: ManimRenderer = ManimRenderer.CAIRO,
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
        return generate_animation(
            self,
            parameters,
            renderer,
            Output.get_filename(output_filename, FileExtension.MOV)
        )