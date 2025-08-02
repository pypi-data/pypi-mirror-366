from yta_validation import PythonValidator
from yta_constants.manim import ManimAnimationType


def validate_is_manim_wrapper_instance_of_type(
    manim_wrapper_instance: 'BaseManimAnimationWrapper',
    type: ManimAnimationType
):
    """
    Validate that the provided 'manim_wrapper_instance'
    is actually an instance of that class and also of
    the given 'type'.

    The wrapper instance contains the parameters needed
    (with their values actually set) and the animation
    generator class that must be called with those
    parameters to generate the animation video.
    """
    if (
        not PythonValidator.is_subclass_of(manim_wrapper_instance, 'BaseManimAnimationWrapper') or
        not PythonValidator.is_an_instance(manim_wrapper_instance)
    ):
        raise Exception('The "text_generator_wrapping_instance" is not a valid instance of a subclass of "BaseManimAnimationWrapper" class.')
    
    type = ManimAnimationType.to_enum(type)

    # Validate the expected type
    # TODO: Isn't this 'not in' (?)
    if type not in manim_wrapper_instance.types:
        raise Exception('The provided "text_generator_wrapping_instance" is not an instance of a manim text generation class.')