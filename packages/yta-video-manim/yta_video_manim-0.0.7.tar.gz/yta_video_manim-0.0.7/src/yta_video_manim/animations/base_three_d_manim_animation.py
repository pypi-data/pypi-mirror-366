from yta_video_manim.config import ManimConfig
from yta_video_manim.animations.utils import generate_animation
from yta_constants.manim import ManimRenderer
from yta_constants.file import FileExtension
from yta_programming.output import Output
from manim import ThreeDScene, config
from abc import abstractmethod
from typing import Union


class BaseThreeDManimAnimation(ThreeDScene):
    """
    General class so that our own classes can inherit it 
    and work correctly.
    """

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
        # the manim engine.s
        pass

    def generate(
        self,
        parameters,
        renderer: ManimRenderer = ManimRenderer.CAIRO,
        output_filename: Union[str, None] = None
    ):
        """
        Generates the animation video file using the provided
        'parameters' and stores it locally as 'output_filename'
        """
        return generate_animation(
            self,
            parameters,
            renderer,
            Output.get_filename(output_filename, FileExtension.MOV)
        )