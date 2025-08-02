from yta_google_drive_downloader.resource import Resource
from manim import *


# TODO: I keep this because I hope one day I can
# call this method from the Manim class correctly
# so I can have the code with a better structure.
# I cannot refactor this because I call this file
# from the terminal when trying to render so it
# has to be in the same file...
def get_magazine_letter(
    letter: str = 'a',
    color: ManimColor = WHITE,
    google_drive_url: str = None,
    background_scale: float = 0.2,
    background_shift: float = 0
):
    """
    Generates the default Mobject Group for our own characters
    """
    # ParameterValidator.validate_mandatory_string('letter', letter, do_accept_empty = False)
    # ParameterValidator.validate_mandatory_string('google_drive_url', google_drive_url, do_accept_empty = False)

    letter = letter[0:1]
    letter = (
        Group(Text('a', font_size = 48, color = color).set_opacity(0))
        if letter == ' ' else
        letter
    )
    
    letter_background_filename = letter
    # We need to use these names because we cannot
    # store files named as '?', '¿', '¡' or '!'
    letter_background_filename = {
        '¿': 'open_question_mark',
        '?': 'close_question_mark',
        '¡': 'open_exclamation_mark',
        '!': 'close_exclamation_mark'
    }[letter]

    TMP_FILENAME = Resource(google_drive_url, 'resources/manim/magazine_letters/' + letter_background_filename + '.svg').file
    letter_background = SVGMobject(TMP_FILENAME).scale(0.2).shift(UP * background_shift)
    letter_text = Text(letter, font_size = 32, color = color)
    letter_group = Group(letter_background, letter_text)
    
    return letter_group