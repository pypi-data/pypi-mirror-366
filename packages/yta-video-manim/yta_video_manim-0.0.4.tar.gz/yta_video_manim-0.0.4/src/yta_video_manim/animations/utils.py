from yta_video_manim.config import ManimConfig
from yta_constants.manim import ManimRenderer
from yta_constants.file import FileExtension
from yta_file.filename.handler import FilenameHandler
from yta_file.handler import FileHandler
from yta_programming.path import DevPathHandler
from yta_programming.output import Output
from manim.cli.render.commands import render as manim_render
from threading import Thread
from typing import Union


def generate_animation(
    instance,
    parameters,
    renderer: ManimRenderer = ManimRenderer.CAIRO,
    output_filename: Union[str, None] = None
):
    """
    The instance must pass the 'self' as 'instance'
    when calling this method.

    This code is here because it was common for
    both of our animation classes.
    """
    output_filename = Output.get_filename(output_filename, FileExtension.MOV)

    renderer = (
        ManimRenderer.CAIRO
        if renderer is None else
        ManimRenderer.to_enum(renderer)
    )
    
    # We write parameters in file to be able to read them
    ManimConfig.write(parameters)

    # Variables we need to make it work
    FPS = str(60)
    CLASS_MANIM_CONTAINER_ABSPATH = DevPathHandler.get_code_abspath(instance.__class__)
    CLASS_FILENAME_WITHOUT_EXTENSION = FilenameHandler.get_file_name(DevPathHandler.get_code_filename(instance.__class__))
    CLASS_NAME = instance.__class__.__name__
    
    output_filename_extension = FilenameHandler.get_extension(output_filename)

    # These args are in 'manim.cli.render.commands.py' injected
    # as '@output_options', '@render_options', etc.
    args = {
        # I never used this 'format' before
        '--format': True,
        output_filename_extension: True, # Valid values are: [png|gif|mp4|webm|mov]
        # Qualities are here: manim\constants.py > QUALITIES
        '--quality': True,
        'h': True,
        '--fps': True,
        FPS: True,
        '--transparent': True,
        '--renderer': True,
        # The 'cairo' default option has been working good always
        renderer.value: True, # 'opengl' or 'cairo', 'cairo' is default
        # The '--output_file' changes the created file name, not the path
        CLASS_MANIM_CONTAINER_ABSPATH: True,
        CLASS_NAME: True
    }

    # TODO: Do more Exception checkings (such as '.smtg')
    if output_filename_extension != 'mov':
        del args['--transparent']

    # We need to execute this as a thread because
    # the program ends when finished if not a thread
    render_thread = Thread(target = manim_render, args = [args])
    render_thread.start()
    render_thread.join()
        
    CREATED_FILE_ABSPATH = f"{DevPathHandler.get_project_abspath()}media/videos/{CLASS_FILENAME_WITHOUT_EXTENSION}/1080p{FPS}/{CLASS_NAME}.{output_filename_extension}"

    FileHandler.rename_file(CREATED_FILE_ABSPATH, output_filename)

    return output_filename