# Copyright (c) 2024 Anas Shakeel

from __future__ import annotations
from sys import stdout
from os import isatty, environ
from re import IGNORECASE, compile as re_compile
from io import UnsupportedOperation
from random import choice, randint
from typing import Literal, Iterable, Union

from ._others import (
    StandardColor,
    Attribute,
    Color256,
    RGBTuple,
    Color,
    ColorMode,
    Quality,
    BGCOLORS_STANDARD,
    FGCOLORS_STANDARD,
    ATTRIBUTES,
    COLORS256_COLORNAMES,
    STANDARD_COLORNAMES,
    ANSI_CODES,
    COLORS_256,
)
from .exceptions import (
    InvalidColorError,
    RGBError,
    HexError,
    StyleError,
    ColorModeError,
)


# Compiled REGEX Patterns
ANSI_REGEX = re_compile(
    r"[\u001B\u009B][\[\]()#;?]*(?:(?:(?:(?:;[-a-zA-Z\d\/#&.:=?%@~_]+)*|[a-zA-Z\d]+(?:;[-a-zA-Z\d\/#&.:=?%@~_]*)*)?\u0007)|(?:(?:\d{1,4}(?:;\d{0,4})*)?[\dA-PR-TZcf-nq-uy=><~]))"
)
HEX_REGEX = re_compile(r"^#?((?:[0-9a-fA-F]{3}){1,2})$", IGNORECASE)
ANSY_STR_REGEX = re_compile(r"(@(?:\w|\d)+\[.*?\])", IGNORECASE)
# ANSY_STR_REGEX with capturing groups
ANSY_STR_CAPT_REGEX = re_compile(r"@((?:\w|\d)+)\[(.*?)\]", IGNORECASE)


# This function is borrowed from 'termcolor' library. licensed under the MIT License.
# Full license text can be found in the THIRD_PARTY_LICENSE file.
def _can_do_colour(*, no_color: bool = None, force_color: bool = None) -> bool:
    """
    Check env vars and for tty/dumb terminal.

    #### First check overrides:
    User-level configuration files and per-instance command-line arguments should
    override `$NO_COLOR`. A user should be able to export `$NO_COLOR` in their shell
    configuration file as a default, but configure a specific program in its
    configuration file to specifically enable color.

    https://no-color.org
    """
    if no_color is not None and no_color:
        return False
    if force_color is not None and force_color:
        return True

    # Then check env vars:
    if "ANSI_COLORS_DISABLED" in environ:
        return False
    if "NO_COLOR" in environ:
        return False
    if "FORCE_COLOR" in environ:
        return True

    # Then check system:
    if environ.get("TERM") == "dumb":
        return False
    if not hasattr(stdout, "fileno"):
        return False

    try:
        return isatty(stdout.fileno())
    except UnsupportedOperation:
        return stdout.isatty()


def colored(
    text: str,
    fgcolor: Color = None,
    bgcolor: Color = None,
    attrs: Iterable[Attribute] = None,
    color_mode: ColorMode = 4,
    *,
    no_color: bool = None,
    force_color: bool = None,
) -> str:
    """
    ### Colored
    Colorize text using `4`, `8`, or `24` bit colors. If `fgcolor`, `bgcolor`, and `attrs` all are `None`,
    the `text` itself is returned without any ansi codes added.

    #### ARGS:
    - `text`: the text to colorize
    - `fgcolor`: the foreground color
    - `bgcolor`: the background color
    - `attrs`: the attributes to apply
    - `color_mode`: the colormode to use (defualt is `4`)

    #### Acceptable `4-bit` colors (Foreground|Background):
        `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`,
        `light_grey`, `dark_grey`, `light_red`, `light_green`, `light_yellow`,
        `light_blue`, `light_magenta`, `light_cyan`.

    #### Acceptable `8-bit` colors (Foreground|Background):
        - `ansy.print_all_colors()` to print all 8-bit colors.
        - `ansy.get_all_colors()` to iterate through all 8-bit colors.

    #### Acceptable `24-bit` colors (Foreground|Background):
        an RGB tuple or Hex color code

    #### Available attributes:
        `bold`, `dark`, `underline`, `blink`, `reverse`, `concealed`,
        `double-underline`, `overline`, `strike`, `italic`

    ```
    # Example
    >> text = 'Hello, ansy!'
    >> colored(text, 'red', 'black', ['bold', 'blink'])
    >>
    >> colored(text, 'plum', color_mode=8)  # 8-bit color: name
    >> colored(text, 215, color_mode=8) # 8-bit color: code
    >>
    >> colored(text, '#B00B1E', color_mode=24) # 24-bit color: Hex
    >> colored(text, (255,100,100), color_mode=24) # 24-bit color: RGB
    ```

    Raises `ColorModeError` if:
    - `color_mode` is invalid

    Raises `InvalidColorError` if:
    - `fgcolor` is invalid
    - `bgcolor` is invalid

    Raises `AttributeError` if:
    - `attrs` contains an invalid attribute

    """
    # Boolean, None, or Empty string would return ""
    if isinstance(text, bool) or text is None or text == "":
        return ""

    result = str(text)

    if not _can_do_colour(no_color=no_color, force_color=force_color):
        return result

    # If no styling requested, return result
    if fgcolor == None and bgcolor == None and attrs == None:
        return result

    return make_ansi(fgcolor, bgcolor, attrs, color_mode) + result + ANSI_CODES["reset"]


def printc(
    text: str,
    fgcolor: Color = None,
    bgcolor: Color = None,
    attrs: Iterable[Attribute] = None,
    color_mode: ColorMode = 4,
    *,
    sep=" ",
    end="\n",
    file=None,
    flush=False,
    no_color: bool = None,
    force_color: bool = None,
):
    """
    ### Print Colored
    Prints whatever returns from `ansy.colored`.

    ```
    # Example
    >> ansy.printc('Print this.', 'light_red', attrs=['bold'])
    ```
    """
    print(
        colored(
            text,
            fgcolor,
            bgcolor,
            attrs,
            color_mode,
            no_color=no_color,
            force_color=force_color,
        ),
        sep=sep,
        end=end,
        file=file,
        flush=flush,
    )


def colored_ansy(
    text: str, style: dict, *, no_color: bool = None, force_color: bool = None
) -> str:
    """
    ### Colored Ansy
    Adds the styling defined in `style` to wherever an `ansy string`
    is found in the `text`.

    #### ARGS:
    - `text`: the text containing the `ansy strings`
    - `style`: a dictionary containing the style(s).

    ##### Style dict:
    `style` is a dictionary that defines the styles to apply to these
    `ansy_strings`. Each style in the `style` dictionary is itself a dictionary.
    Purpose of this structure is so that you could define all your styles in one
    dictionary and then use it everywhere, instead of creating a dictioanry for
    each style and create a mess in your code.

    ```
    # Example Usage
    >> style = {
    ..     "my_style": {
    ..         "color_mode": 24,
    ..         "fgcolor": (200,100,50),
    ..         "bgcolor": '#121212',
    ..         "attrs": ["bold", "reverse"]
    ..     }
    .. }
    >>
    >> # Style can also be created by create_style()
    >> style['new_style'] = ansy.create_style(24, 'fff', (200,0,0), attrs=['bold'])
    >>
    >> ansy.colored_ansy("This is an @new_style[ansy string]", style)
    'This is an ansy string'
    >> # above string is formatted as defined by "new_style"
    ```
    `style` dictionary can have as many styles as you want, just make sure you use
    the same name for the style in `ansy string` as defined in `style`

    Raises `StyleError` if:
    - style used in `ansy string` not found in `style` dict

    Raises `ColorModeError` if:
    - `color_mode` provided in style, is invalid

    """
    # Find all ansy_strings and split them
    matches: list = ANSY_STR_REGEX.split(text)
    if not matches:
        return None

    parsed = [""] * len(matches)
    for index, m in enumerate(matches):
        # Parse, format and add into the parsed:list
        parsed[index] = _parse_ansy(
            m, style, no_color=no_color, force_color=force_color
        )

    return "".join(parsed)


def _parse_ansy(
    ansy: str, style: dict, *, no_color: bool = None, force_color: bool = None
) -> str:
    """
    Parse `ansy` string and return the formatted ansy.

    #### ARGS:
    - `ansy`: the ansy string
    - `style`: the styles dictionary which contains the styles (formats if style found, raises `ValueError` otherwise)
    """
    if ansy_matches := ANSY_STR_CAPT_REGEX.match(ansy):
        # Parse ansy_matches and apply formatting
        if ansy_matches.group(1) not in style:
            err = f"Undefined style: '{ansy_matches.group(1)}'"
            raise StyleError(err)

        # Style dict for currently matched ansy_string
        current_style: dict = style[ansy_matches.group(1)]

        # Colorize the ansy strings
        return colored(
            ansy_matches.group(2),
            current_style["fgcolor"],
            current_style["bgcolor"],
            current_style["attrs"],
            current_style["color_mode"],
            no_color=no_color,
            force_color=force_color,
        )

    # Returns the string if not ansy
    return ansy


def create_style(
    color_mode: ColorMode = 4,
    fgcolor: Color = None,
    bgcolor: Color = None,
    attrs: Iterable[Attribute] = None,
) -> dict:
    """
    ### Create Style
    Creates a style `dict` to use in `colored_ansy()` as style.

    Sole purpose of this function is to make the process creating a style easier
    and safer. it validates the `fgcolor`, `bgcolor` and `attrs` to make
    sure they are valid.

    #### ARGS:
    - `color_mode`: the color mode (`4-bit`, `8-bit`, `24-bit`)
        - `4` means use 4-bit colors (`16` Standard colors)
        - `8` means use 8-bit colors (`256` colors)
        - `24` means use 24-bit colors (approx. `16.7 million` colors)
    - `fgcolor`: the foreground color
    - `bgcolor`: the background color
    - `attrs`: the attributes list

    ```
    >> # Example Usage
    >> fg = (255,100,100)
    >> bg = (50,0,50)
    >> attrs = ["bold", "underline"]
    >> styles['my_style'] = ansy.create_style(24, fg, bg, attrs)
    >> styles
    {
        "my_style": {
            "color_mode": 24,
            "fgcolor": (255,100,100),
            "bgcolor": (50,0,50),
            "attrs": ["bold", "underline"]
        }
    }
    ```

    Raises `InvalidColorError` if:
    - `fgcolor` is not a valid color
    - `bgcolor` is not a valid color

    Raises `ColorModeError` if:
    - `color_mode` is invalid

    Raises `AttributeError` if:
    - `attrs` includes an invalid attribute string

    """
    # Invalid color_mode ?
    if not _is_valid_colormode(color_mode):
        raise ColorModeError(f"Invalid color_mode: {color_mode}")

    # Color Validation
    fgcolor, bgcolor = _validate_colors((fgcolor, bgcolor), color_mode)

    # Attributes Valiadation
    attrs = _validate_attrs(attrs)

    # Create the dictionary
    return {
        "color_mode": color_mode,
        "fgcolor": fgcolor,
        "bgcolor": bgcolor,
        "attrs": attrs,
    }


def colored_gradient(
    text: str,
    start_color: Union[RGBTuple, str],
    end_color: Union[RGBTuple, str],
    quality: Quality = "medium",
    reverse: bool = False,
) -> str:
    """
    ### Colored Gradient (24-bit)
    Apply horizontal gradient on `text`.

    ##### NOTE:
    This method (when `quality` is high) assigns a color (ANSI sequence for RGB colors) to each character of text.
    an ANSI Sequence for one RGB color can be from `17` to `23` characters long.

    It goes like: `len(text) * 17 or 23`.

    So if input `text` is 10 characters long, output text will be
    approx. `170` or `230` characters long!

    An input of `64 characters` outputs approx. `1,472 characters`.
    ##### Point being: Use higher quality only when necessary!

    #### ARGS:
    - `text`: the text to apply the gradient to
    - `start_color`: starting foreground color (`RGBTuple` or `Hex code`)
    - `end_color`: ending foreground color (`RGBTuple` or `Hex code`)
    - `quality`: quality of the gradient (choose from `high`, `medium`, or `low`)
    - `reverse`: reverses the gradient to be (right to left) instead.

    Raises `InvalidColorError` if:
    - `start_color` is an invalid `24-bit` color
    - `end_color` is an invalid `24-bit` color

    Raises `AssertionError` if:
    - `quality` is not set to `high` or `medium` or `low`
    - `start_color` or `end_color` are `None`
    """
    if not text:
        return ""

    assert (
        start_color != None or end_color != None
    ), "start_color and end_color must not be None"

    # Colors Validation
    start_color, end_color = _validate_colors((start_color, end_color), 24)

    # Convert to RGBs, if Hexcodes
    start_color = start_color if is_valid_rgb(start_color) else hex_to_rgb(start_color)
    end_color = end_color if is_valid_rgb(end_color) else hex_to_rgb(end_color)

    assert quality in ("high", "medium", "low")

    # Length of text
    text_length = len(text)

    # Create the gradient (Generator not actual values)
    gradient = make_gradient(start_color, end_color, text_length, reverse=reverse)

    batch_size = 1
    if quality == "low":
        batch_size = len(text) // 4
    elif quality == "medium":
        batch_size = len(text) // 8
    else:
        # High quality, already set
        pass

    # Clip batch size
    batch_size = max(batch_size, 1)  # to 1, if less...
    batch_size = min(batch_size, text_length)  # to text_length, if more...

    # Apply the gradient
    return _apply_gradient(text, gradient, batch_size)


def _apply_gradient(text: str, gradient: list, batch_size: int) -> str:
    """Apply `gradient` to `text`"""
    fmt_str = ANSI_CODES["24bit"]
    gradient_text = ""
    read_chars = 0
    batch = []

    # Iterate through the text and gradient
    for char, color in zip(text, gradient):
        batch.append(char)  # Add char to batch
        read_chars += 1

        # Is batch full?
        if len(batch) == batch_size:
            gradient_text += fmt_str % (38, *color, "".join(batch))
            batch = []  # Start new batch
            continue

        # Is this last batch?
        if read_chars >= len(text):
            gradient_text += fmt_str % (38, *color, "".join(batch))

    return gradient_text + ANSI_CODES["reset"]


def make_gradient(
    start_color: RGBTuple, end_color: RGBTuple, steps: int = 10, reverse: bool = False
):
    """
    ### Make Gradient (24-bit)
    Make a gradient between two RGB colors `start_color` and `end_color` by
    linearly interpolating between these colors for a given number of `steps`.
    Returns a `generator object`.

    #### ARGS:
    - `start_color`: starting rgb color
    - `end_color`: ending rgb color
    - `steps`: steps to interpolate across (minimum `2`)
    - `reverse`: flip the gradient horizontally

    ```
    # Example
    >> start_color = (240, 194, 123)
    >> end_color = (255, 85, 85)
    >> gradient = ansy.make_gradient(start_color, end_color, steps=4)
    >>
    >> gradient
    <generator object make_gradient at 0x0000018F0B580700>
    >>
    >> list(gradient)
    [(240, 194, 123), (245, 157, 110), (250, 121, 97), (255, 85, 85)]
    ```

    Raises `InvalidColorError` if:
    - `start_color` is not a valid RGBTuple
    - `end_color` is not a valid RGBTuple
    """
    # Validate the RGBs
    if start_color and not is_valid_rgb(start_color):
        raise InvalidColorError(f"Invalid RGB: {start_color}")
    if end_color and not is_valid_rgb(end_color):
        raise InvalidColorError(f"Invalid RGB: {end_color}")

    # Clip steps to 2 if lesser.
    steps = 2 if steps < 2 else steps

    # Flip the colors, if asked...
    if reverse:
        start_color, end_color = end_color, start_color

    # Generate the gradient colors
    for step in range(steps):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (step / (steps - 1)))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (step / (steps - 1)))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (step / (steps - 1)))

        yield (r, g, b)


def colored_random(
    text: str,
    target: Literal["all", "words", "chars"] = "all",
    color_mode: ColorMode = 4,
    custom_palette: Iterable = None,
    attrs: Iterable[Attribute] = None,
    random_attrs: bool = False,
) -> str:
    """
    ### Colored Random
    Apply a random color to `text`. colors are chosen from a colorsystem specified by `color_mode`.

    #### ARGS:
    - `text`: the text string
    - `target`: apply random colors to `chars`, `words` or `all` string.
    - `color_mode`: the colormode to use
    - `custom_palette`: iterable of user-defined colors (default is `None` which uses random colors from the whole range of colors)
    - `attrs`: the attributes to apply (attributes are NOT randomized by default)
    - `random_attrs`: whether to apply attributes randomly or not

    ```
    # Example
    >> text = 'This is just a string.'
    >> ansy.colored_random(text, 'all', 4)
    'This is just a string.' # This is randomly colored
    >>
    >> text = 'This is just a string.'
    >> ansy.colored_random(text, 'words', 4)
    'This is just a string.'
    >>
    >> palette = ['light_red', 'blue']
    >> ansy.colored_random(text, 'words', 4, palette)
    'This is just a string.'
    >>
    >> # Not recommended to use 'chars' with 24bit colors, if string is longer than 50 characters
    >> ansy.colored_random(text, 'chars', 24)
    'This is just a string.'
    >>
    >> # Why not you might ask! let me show you
    >> f = ansy.colored_random('This', 'chars', 24)
    >> print([f])
    ['\x1b[38;2;5;155;190mT\x1b[0m\x1b[38;2;119;11;99mh\x1b[0m\x1b[38;2;24;50;220mi\x1b[0m\x1b[38;2;178;45;244ms\x1b[0m']
    >>
    >> # for a string of 4 characters, it outputs 113 characters! and for what? just to see some random colors in the terminal?
    ```

    Raises `ValueError` if:
    - `target` is not set to `'chars'`, `'words'`, `'all'`

    Raises `ColorModeError` if:
    - `color_mode` is invalid

    Raises `InvalidColorError` if:
    - `custom_palette` contains an invalid color

    Raises `AttributeError` if:
    - `attrs` contains an invalid attribute

    """
    if not text:
        return ""

    # Palette Validation
    if custom_palette:
        _validate_colors(custom_palette, color_mode)

    # Attrs validation
    attrs = _validate_attrs(attrs)

    # Break the text
    if target == "chars":
        broken_text: list = list(text)  # Into letters
    elif target == "words":
        broken_text: list = text.split(" ")  # Into words
    elif target == "all":
        broken_text: list = [text]  # Whole text
    else:
        # Raise error
        raise ValueError("target must be 'chars', 'words' or 'all'")

    colorized_items: list = [""] * len(broken_text)
    for i, chunk in enumerate(broken_text):
        colorized_items[i] = _apply_random_colors(
            chunk, color_mode, custom_palette, attrs, random_attrs
        )
    # Join separator
    sep = ""
    if target == "words":
        sep = " "

    return sep.join(colorized_items)


def _apply_random_colors(
    text: str,
    color_mode: ColorMode,
    custom_palette: Iterable,
    attrs: Iterable[Attribute],
    random_attrs: bool,
) -> str:
    """Apply random colors and/or attributes"""
    # Choose a random color or from palette
    if custom_palette is not None:
        color = choice(custom_palette)
    else:
        color = get_random_color(color_mode)

    # Choose random attribute
    new_attrs = [choice(attrs)] if (attrs and random_attrs) else attrs

    # Format current item (word or char)
    return colored(text, color, color_mode=color_mode, attrs=new_attrs)


def get_random_color(color_mode: ColorMode = 4) -> Union[str, RGBTuple]:
    """
    ### Get Random Color
    Returns a random color from a colorsystem specified by `color_mode`.

    #### Values Returned for each colormode:
    - `4`: Returns the name of a 4-bit color
    - `8`: Returns the name of an 8-bit color
    - `24`: Returns the `RGBTuple`

    ```
    # Example
    >> ansy.get_random_color(4)
    'light_green'
    >> ansy.get_random_color(8)
    'plum'
    >> ansy.get_random_color(24)
    (184, 30, 57)
    ```

    Raises `ColorModeError` if:
    - `color_mode` is invalid.

    """
    if color_mode == 4:
        # Choose a random 4bit color
        return choice(STANDARD_COLORNAMES)
    elif color_mode == 8:
        # Choose a random 8bit color
        return choice(COLORS256_COLORNAMES)
    elif color_mode == 24:
        # Create a random RGBTuple
        return (randint(0, 255), randint(0, 255), randint(0, 255))
    else:
        # Raise error
        raise ColorModeError(f"Invalid color_mode: {color_mode}")


def create_random_palette(color_mode: ColorMode, n: int) -> list:
    """
    ### Create Palette
    Returns a list of colors from `color_mode`-bit color system.

    #### ARGS:
    - `color_mode`: the colormode to use
    - `n`: number of colors to include in palette

    Raises `TypeError` if:
    - `n`: is not an integer
    """
    if type(n) != int:
        raise TypeError("n is expected to be an integer.")
    return [get_random_color(color_mode) for _ in range(n)]


def de_ansi(text: str) -> str:
    """
    ### De-Ansi
    Removes all ansi codes from `text`. It uses `ANSI_REGEX` pattern.
    Returns the `text` as is, If no ANSI sequences found.

    #### ARGS:
    - `text`: the text to de_ansi-fy

    ```
    # Example
    >> # Ansi containting string
    >> ansi_string = colored("This is clean.", "red", "white", ["bold", "dark"])
    >>
    >> de_ansi(ansi_string)
    'This is clean.'
    ```

    Raises `TypeError` if:
    - `text` is not a `str` object
    """
    if not isinstance(text, str):
        raise TypeError(f"'text' is expected to be str: not {type(text)}")

    # Recognize all ANSI Patterns in a string
    return ANSI_REGEX.sub("", text)


def contains_ansi(text: str) -> bool:
    """
    ### Contains ansi
    Returns `True` if text contains ansi codes, else `False`.

    #### Example:
    ```
    >> text = colored("Formatted String", fgcolor="red")
    >> contains_ansi(text)
    True
    >> text = de_ansi(text)
    >> contains_ansi(text)
    False
    ```
    """
    return True if ANSI_REGEX.search(text) else False


def print_all_colors():
    """
    ### Print All Colors
    Print all 256 colors with their name and code.
    (sorted by codes in asc. order)
    """
    for code, clr in sorted(zip(COLORS_256.values(), COLORS_256.keys())):
        print(
            " ",
            colored("    ", bgcolor=clr, color_mode=8),
            f"{colored(code, code, color_mode=8)}: {clr}",
        )


def get_all_colors(sort_by_name: bool = False):
    """
    ### Get All Colors
    Yields a `tuple` of `color_name` and it's `code`. (sorted by `code`)

    These colors include `16` Standard Colors, `216` Extended
    Colors, and Remaining `24` Colors are Greyscale.

    #### ARGS:
    - `sort_by_name`: Sorts colors by name (default is `False` which sorts by code)

    ```
    # Example Usage
    >> from ansy import get_all_colors
    >> for color, code in get_all_colors():
    >>     print(f"{color}, {code}")
    aquamarine, 79
    aquamarine_1, 86
    --snip--
    yellow_pale, 187
    ```
    """
    zipped = zip(COLORS_256.values(), COLORS_256.keys())
    if sort_by_name:
        zipped = zip(COLORS_256.keys(), COLORS_256.values())

    for c1, c2 in sorted(zipped):
        if sort_by_name:
            yield c1, c2
        else:
            yield c2, c1


def search_colors(query: str):
    """
    ### Search [8-bit] Colors
    Yields all colors (`name`, `code`) that contain `query` in their name.

    #### ARGS:
    - `query`: the string to look for...
    """
    if not query:
        return None

    for clr, code in get_all_colors(True):
        if query in clr:
            yield clr, code


def make_ansi(
    fgcolor: Color = None,
    bgcolor: Color = None,
    attrs: Iterable[Attribute] = None,
    color_mode=4,
) -> str:
    """
    ### Make Ansi
    Make an `Ansi Escape Sequence` from the args given.
    Returns the sequence without `Ansi Reset Code`.

    #### ARGS:
    - `fgcolor`: the foreground color (any color that belongs to `color_mode`)
    - `bgcolor`: the background color (any color that belongs to `color_mode`)
    - `attrs`: the attributes
    - `color_mode`: the color mode to use

    ```
    # Example
    >> ansy.make_ansi("light_green", "dark_grey", color_mode=4)
    >> ansy.make_ansi(19, "plum", attrs=['bold', 'italic'], color_mode=8)
    >> ansy.make_ansi("#A22", (50,50,100), color_mode=24)
    ```

    Raises `InvalidColorError` if:
    - `fgcolor` is invalid according to color_mode
    - `bgcolor` is invalid according to color_mode

    Raises `ColorModeError` if:
    - `color_mode` is invalid
    """
    if not _is_valid_colormode(color_mode):
        raise ColorModeError(f"Invalid color_mode: {color_mode}")

    # Color validation
    fgcolor, bgcolor = _validate_colors((fgcolor, bgcolor), color_mode)

    # Attrs validation
    attrs = _validate_attrs(attrs)

    # Normalizing the colors to be used in ANSI codes
    if fgcolor:
        fgcolor = _normalize_color(fgcolor, color_mode)
    if bgcolor:
        bgcolor = _normalize_color(bgcolor, color_mode, True)

    result = ""
    fmt_str = ANSI_CODES[f"{color_mode}bit"]

    # Adding Colors
    if color_mode == 4:
        if fgcolor:
            result = fmt_str % (fgcolor, result)

        if bgcolor:
            result = fmt_str % (bgcolor, result)

    elif color_mode == 8:
        if fgcolor:
            result = fmt_str % (38, fgcolor, result)

        if bgcolor:
            result = fmt_str % (48, bgcolor, result)

    else:  # 24-bit
        if fgcolor:
            result = fmt_str % (38, *fgcolor, result)

        if bgcolor:
            result = fmt_str % (48, *bgcolor, result)

    # Adding Attributes
    if attrs:
        for a in attrs:
            result = ANSI_CODES["attr"] % (ATTRIBUTES[a], result)

    return result


def _normalize_color(color: Color, color_mode: ColorMode, bg: bool = False) -> Color:
    """
    Normalize `color` to be used in ansi escape sequences.
    Normalized colors are safe to use in ansi sequences
    without any additional validations.

    #### NOTE:
    Caller is responsible for validating the colors.
    This method throws errors otherwise.

    #### ARGS:
    - `color` : the color to normalize
    - `color_mode` : the colormode to use
    - `bg` : normalize as `BG` color? only applicable on 4-bit color_mode
    """

    if color_mode == 4:
        return BGCOLORS_STANDARD[color] if bg == True else FGCOLORS_STANDARD[color]

    elif color_mode == 8:
        return colorname_to_code(color)

    elif color_mode == 24:
        return hex_to_rgb(color) if is_valid_hex(color) else color
    else:
        return None


def _validate_colors(colors: tuple, color_mode: ColorMode) -> tuple:
    """
    ### Validate Colors
    Validate the colors based on `color_mode`. returns the `colors` if all good.

    #### Syntax for `colors`:
    - `(fgcolor, bgcolor, someothercolor, etc_color)`

    ```
    # Example
    >> fgcolor, bgcolor = 'light_red', None
    >> _validate_colors((fgcolor, bgcolor), color_mode=4)
    ('light_red', None)
    >>
    >> _validate_colors(('light_red', 'invalid_color'), color_mode=8)
    InvalidColorError: Invalid 8-bit color: invalid_color
    ```

    Raises `InvalidColorError` if:
    - `color` is invalid
    """
    for color in colors:
        if color != None and not is_valid_color(color, color_mode):
            err = f"Invalid {color_mode}-bit color: {color}"
            raise InvalidColorError(err)

    return colors


def _validate_attrs(attrs: Iterable[Attribute]) -> list:
    """
    ### Validate Attrs
    Validate the `attrs`. returns the `attrs` if all good.

    ```
    # Example
    >> _validate_attrs(['bold', 'italic'])
    ['bold', 'italic']
    >>
    >> _validate_attrs(['underline', 'invalid_attr'])
    AttributeError: Invalid attribute: invalid_attr
    ```

    Raises `AttributeError` if:
    - `attrs` contais an invalid attribute
    """
    if attrs:
        for attr in attrs:
            if not is_valid_attr(attr):
                err = f"Invalid attribute: {attr}"
                raise AttributeError(err)

    return attrs


def _is_valid_colormode(color_mode: ColorMode) -> bool:
    """Validates colormode, Returns `True` if valid, `False` otherwise"""
    if color_mode in (4, 8, 24):
        return True
    return False


def _is_color_8bit(color: Union[int, str]) -> bool:
    """
    Returns `True` if `clr` is a recognized color, else `False`.

    - `clr`: a color name or code (from 256 color system)
    """
    if not isinstance(color, (int, str)):
        return False

    if color in COLORS_256 or color in COLORS_256.values():
        # If color name OR color code
        return True

    return False


def is_valid_color(color: Color, color_mode: ColorMode) -> bool:
    """
    ### Is Valid Color?
    validates the color based on `color_mode`. Returns `True` if color
    is valid, `False` for otherwise.

    #### ARGS:
    - `color`: the color to validate
    - `color_mode`: the color mode of `color` (can be `4`, `8`, `24`)
    """
    if color_mode == 4:
        return color in STANDARD_COLORNAMES
    elif color_mode == 8:
        return _is_color_8bit(color)
    elif color_mode == 24:
        return is_valid_rgb(color) or is_valid_hex(color)
    else:
        return False


def is_valid_rgb(rgb: RGBTuple) -> bool:
    """
    ### Is valid rgb
    Returns `True` if `rgb` is valid rgb, else `False`.
    `rgb` must be a `tuple` not `list`, not `set` not anything else.

    #### Valid RGB:
    RGB tuple is valid if:
    - There are three integer values.
    - `R` is an int from `[0-255]`
    - `G` is an int from `[0-255]`
    - `B` is an int from `[0-255]`

    #### ARGS:
    - `rgb`: the rgb tuple to validate

    """
    # Must be a tuple
    if not isinstance(rgb, tuple):
        return False

    # Must have 3 values
    if len(rgb) != 3:
        return False

    # Must lie in range 0-255
    for v in rgb:
        if type(v) != int or v > 255 or v < 0:
            return False

    return True


def is_valid_hex(hexcode: str) -> bool:
    """
    ### Is valid hex
    Returns `True` if `hexcode` is valid hex color code, else `False`.

    #### ARGS:
    - `hexcode`: the hex color code to validate
    """
    # Must be a str
    if type(hexcode) != str:
        return False

    if HEX_REGEX.match(hexcode):
        return True

    return False


def is_valid_attr(attr: Attribute) -> bool:
    """
    ### Is valid attr
    Returns `True` if `attr` is a valid Attribute, else `False`.

    #### ARGS:
    - `attr`: the attribute string

    #### Valid Attributes:
    `bold`, `dark`, `underline`, `blink`, `reverse`, `concealed`,
    `double-underline`, `overline`, `strike`, `italic`

    ```
    # Example
    >> is_valid_attr('bold')
    True
    >> is_valid_attr('ansy')
    False
    ```
    """
    if attr in ATTRIBUTES:
        return True

    return False


def colorname_to_code(color: Color256) -> Union[int, None]:
    """
    ### Colorname to Code
    Returns the `code` for the `color`.
    Returns `None` if color is not a valid 8-bit color.
    If `color` is already an 8-bit color code, returns the code.

    #### ARGS:
    - `color`: name of a color (from 256 color system)

    ```
    # Example
    >> colorname_to_code("red")
    1
    >> colorname_to_code("red-ish")
    None
    >> colorname_to_code(1)
    1
    >> colorname_to_code(300)
    None
    ```

    #### FunFact:
    This method raises no errors whatsoever!
    """
    if not is_valid_color(color, 8):
        return None

    return COLORS_256.get(color, color)


def code_to_colorname(color: int) -> Union[str, None]:
    """
    ### Code to Colorname
    Returns the color name for the `color` code.
    Returns `None` if color is not a valid color. If `color` is already a valid
    colorname, Returns the name.

    #### ARGS:
    - `color`: code of a color (from 256 color system `i.e. [0-255]`)

    ```
    # Example
    >> code_to_colorname(1)
    'red'
    >> code_to_colorname(-2)
    None
    >> code_to_colorname("blue")
    'blue'
    ```

    #### FunFact:
    This method raises no errors whatsoever!

    """
    # Ensure color is valid
    if not is_valid_color(color, 8):
        return None

    # Search colorcode, return if found
    for clr, c in COLORS_256.items():
        if c == color:
            return clr

    # At this point, its a valid color but not a code,
    # means its already a colorname
    return color


def hex_to_rgb(hexcode: str) -> RGBTuple:
    """
    ### Hex to RGB
    Converts a `hex` color code into an `RGB tuple`.
    It is case-insensitive and also recognizes 3-lettered hex
    color codes `e.g #FFF, #9ca etc.`

    #### Valid HEX Color Code:
    - `#` symbol is optional
    - length must either be `3` or `6` (excluding `#` symbol)
    - each letter must only be 0-9, a-f
    - case-insensitive

    #### ARGS:
    - `hexcode`: a hex color code string

    ```
    # Example
    >> ansy.hex_to_rgb("#FFFFFF")
    (255, 255, 255)
    >> ansy.hex_to_rgb("Fff")
    (255, 255, 255)
    ```

    Raises `HexError` if:
    - `hexcode` is not a valid hex color code
    """
    if not is_valid_hex(hexcode):
        raise HexError(f"Invalid hexcode: {hexcode}")

    new_hex = hexcode.lstrip("#")  # Strip the hash

    # Convert to 6-letter hex (if not already)
    if len(new_hex) == 3:
        new_hex = "".join([l + l for l in new_hex])

    # Convert the hex to RGB
    return tuple(int(new_hex[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: RGBTuple, with_symbol: bool = True) -> str:
    """
    ### RGB to Hex
    Converts an `rgb` tuple into Hex color code.

    #### ARGS:
    - `rgb`: RGB tuple to convert to hex
    - `with_symbol`: Whether to include the `#` symbol in output

    ```
    # Example
    >> ansy.hex_to_rgb((255,255,255), with_symbol=True)
    "#FFFFFF"
    >> ansy.hex_to_rgb((0,0,0), with_symbol=False)
    "000000"
    ```

    Raises `RGBError` if:
    - `rgb` is not a valid RGB tuple
    """
    # Validate the RGB tuple
    if not is_valid_rgb(rgb):
        raise RGBError(f"rgb {rgb} is not a valid RGB tuple.")

    # Conversion...
    hexcode = "#" if with_symbol else ""
    for value in rgb:
        h = format(value, "X")  # Convert to hex
        if len(h) == 1:
            h = "0" + h  # Add zero before the hex if length:1
        hexcode += h

    return hexcode
