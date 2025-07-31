""" Run `pytest test_ansy.py` """

import ansy
from ansy.exceptions import *
from typing import Generator
from pytest import raises


def test_colored_basic():
    assert ansy.colored(0, "blue", force_color=True) == "\x1b[34m0\x1b[0m"

    assert ansy.colored(None, "blue", force_color=True) == ""
    assert ansy.colored("", "blue", force_color=True) == ""
    assert ansy.colored(False, "blue", force_color=True) == ""

    s = "This is string."
    # 4Bit
    assert ansy.colored(s, "blue", force_color=True) == "\x1b[34mThis is string.\x1b[0m"
    assert (
        ansy.colored(s, "blue", "dark_grey", force_color=True)
        == "\x1b[100m\x1b[34mThis is string.\x1b[0m"
    )

    # 8Bit
    assert (
        ansy.colored(s, "blue", color_mode=8, force_color=True)
        == "\x1b[38;5;4mThis is string.\x1b[0m"
    )
    assert (
        ansy.colored(s, "plum", 234, color_mode=8, force_color=True)
        == "\x1b[48;5;234m\x1b[38;5;183mThis is string.\x1b[0m"
    )

    # 24Bit
    assert (
        ansy.colored(s, (255, 100, 100), "#FFF", color_mode=24, force_color=True)
        == "\x1b[48;2;255;255;255m\x1b[38;2;255;100;100mThis is string.\x1b[0m"
    )
    assert (
        ansy.colored(s, "#FFFFFF", (50, 50, 100), color_mode=24, force_color=True)
        == "\x1b[48;2;50;50;100m\x1b[38;2;255;255;255mThis is string.\x1b[0m"
    )


def test_colored_advanced():
    assert (
        ansy.colored(
            "This is string.",
            "blue",
            attrs=["bold", "italic", "strike", "overline", "underline"],
            force_color=True,
        )
        == "\x1b[4m\x1b[53m\x1b[9m\x1b[3m\x1b[1m\x1b[34mThis is string.\x1b[0m"
    )
    assert (
        ansy.colored(
            "This is string.",
            "blue",
            "dark_grey",
            attrs=["bold", "italic", "strike", "overline", "underline"],
            force_color=True,
        )
        == "\x1b[4m\x1b[53m\x1b[9m\x1b[3m\x1b[1m\x1b[100m\x1b[34mThis is string.\x1b[0m"
    )
    assert (
        ansy.colored(
            "This is string.",
            "blue",
            color_mode=8,
            attrs=["bold", "italic", "strike", "overline", "underline"],
            force_color=True,
        )
        == "\x1b[4m\x1b[53m\x1b[9m\x1b[3m\x1b[1m\x1b[38;5;4mThis is string.\x1b[0m"
    )
    assert (
        ansy.colored(
            "This is string.",
            "plum",
            234,
            color_mode=8,
            attrs=["bold", "italic", "strike", "overline", "underline"],
            force_color=True,
        )
        == "\x1b[4m\x1b[53m\x1b[9m\x1b[3m\x1b[1m\x1b[48;5;234m\x1b[38;5;183mThis is string.\x1b[0m"
    )
    assert (
        ansy.colored(
            "This is string.",
            (255, 100, 100),
            "#FFF",
            color_mode=24,
            attrs=["bold", "italic", "strike", "overline", "underline"],
            force_color=True,
        )
        == "\x1b[4m\x1b[53m\x1b[9m\x1b[3m\x1b[1m\x1b[48;2;255;255;255m\x1b[38;2;255;100;100mThis is string.\x1b[0m"
    )
    assert (
        ansy.colored(
            "This is string.",
            "#FFFFFF",
            (50, 50, 100),
            color_mode=24,
            attrs=["bold", "italic", "strike", "overline", "underline"],
            force_color=True,
        )
        == "\x1b[4m\x1b[53m\x1b[9m\x1b[3m\x1b[1m\x1b[48;2;50;50;100m\x1b[38;2;255;255;255mThis is string.\x1b[0m"
    )


def test_colored_errors():
    s = "this is a string"
    with raises(ColorModeError):
        ansy.colored(s, "blue", force_color=True, color_mode=18)

    with raises(InvalidColorError):
        ansy.colored(s, "plum", force_color=True, color_mode=4)
    with raises(InvalidColorError):
        ansy.colored(s, bgcolor="invalid", force_color=True, color_mode=8)
    with raises(InvalidColorError):
        ansy.colored(s, "#fva", force_color=True, color_mode=24)
    with raises(InvalidColorError):
        ansy.colored(s, bgcolor=(255, 502, 10), force_color=True, color_mode=24)

    with raises(AttributeError):
        ansy.colored(s, attrs=["old"], force_color=True, color_mode=24)


def test_colored_ansy():
    style = {
        "yellow": ansy.create_style(24, fgcolor="#f0c27b"),
        "red": ansy.create_style(24, fgcolor="#ff5555"),
        "new": ansy.create_style(24, bgcolor="#ff5555", attrs=["italic", "bold"]),
        "invalid": {
            "color_mode": 54,
            "fgcolor": "343434",
            "bgcolor": None,
            "attrs": None,
        },
    }
    assert (
        ansy.colored_ansy("Welcome to @red[ansy] @yellow[:)]", style, force_color=True)
        == "Welcome to \x1b[38;2;255;85;85mansy\x1b[0m \x1b[38;2;240;194;123m:)\x1b[0m"
    )

    with raises(StyleError):
        ansy.colored_ansy("Welcome to @red[ansy] @asd[:)]", style, force_color=True)

    with raises(ColorModeError):
        ansy.colored_ansy("Welcome to @red[ansy] @invalid[:)]", style, force_color=True)


def test_colored_gradient():
    assert (
        ansy.colored_gradient("asd", (25, 25, 100), (1, 1, 1))
        == "\x1b[38;2;25;25;100ma\x1b[38;2;13;13;50ms\x1b[38;2;1;1;1md\x1b[0m"
    )
    assert (
        ansy.colored_gradient("asd", (25, 25, 100), (1, 1, 1), reverse=True)
        == "\x1b[38;2;1;1;1ma\x1b[38;2;13;13;50ms\x1b[38;2;25;25;100md\x1b[0m"
    )
    assert (
        ansy.colored_gradient("a", (25, 25, 100), (1, 1, 1))
        == "\x1b[38;2;25;25;100ma\x1b[0m"
    )
    assert (
        ansy.colored_gradient("This is quality test", "#ff22ff", "b00b1e", "high")
        == "\x1b[38;2;255;34;255mT\x1b[38;2;250;32;243mh\x1b[38;2;246;31;231mi\x1b[38;2;242;30;219ms\x1b[38;2;238;29;207m \x1b[38;2;234;27;195mi\x1b[38;2;230;26;183ms\x1b[38;2;225;25;172m \x1b[38;2;221;24;160mq\x1b[38;2;217;23;148mu\x1b[38;2;213;21;136ma\x1b[38;2;209;20;124ml\x1b[38;2;205;19;112mi\x1b[38;2;200;18;101mt\x1b[38;2;196;17;89my\x1b[38;2;192;15;77m \x1b[38;2;188;14;65mt\x1b[38;2;184;13;53me\x1b[38;2;180;12;41ms\x1b[38;2;176;11;30mt\x1b[0m"
    )
    assert (
        ansy.colored_gradient("This is quality test", "#ff22ff", "b00b1e", "medium")
        == "\x1b[38;2;250;32;243mTh\x1b[38;2;242;30;219mis\x1b[38;2;234;27;195m i\x1b[38;2;225;25;172ms \x1b[38;2;217;23;148mqu\x1b[38;2;209;20;124mal\x1b[38;2;200;18;101mit\x1b[38;2;192;15;77my \x1b[38;2;184;13;53mte\x1b[38;2;176;11;30mst\x1b[0m"
    )
    assert (
        ansy.colored_gradient("This is quality test", "#ff22ff", "b00b1e", "low")
        == "\x1b[38;2;238;29;207mThis \x1b[38;2;217;23;148mis qu\x1b[38;2;196;17;89mality\x1b[38;2;176;11;30m test\x1b[0m"
    )

    with raises(InvalidColorError):
        ansy.colored_gradient("asd", (25, 25, 1000), (1, 1, 1))

    with raises(InvalidColorError):
        ansy.colored_gradient("asd", (25, 25, 100), (1, 1, -1))

    with raises(AssertionError):
        ansy.colored_gradient("asd", (25, 25, 100), (1, 1, 1), "2")


def test_make_ansi():
    with raises(ColorModeError):
        ansy.make_ansi(bgcolor="light_red", color_mode="24")
    with raises(ColorModeError):
        ansy.make_ansi(bgcolor="light_red", color_mode=256)
    with raises(ColorModeError):
        ansy.make_ansi(bgcolor="light_red", color_mode=-4)
    with raises(AttributeError):
        ansy.make_ansi(attrs=["something", "invalid"])


def test_make_ansi_4bit():
    # Expected...
    e = "\x1b[53m\x1b[1m\x1b[100m\x1b[32m"
    # Created...
    f = ansy.make_ansi("green", "dark_grey", ["bold", "overline"], 4)
    assert f == e

    with raises(InvalidColorError):
        ansy.make_ansi(fgcolor="asdf", color_mode=4)
    with raises(InvalidColorError):
        ansy.make_ansi(fgcolor="light_ref", color_mode=4)
    with raises(InvalidColorError):
        ansy.make_ansi(fgcolor="bla", color_mode=4)
    with raises(InvalidColorError):
        ansy.make_ansi(fgcolor=33, color_mode=4)


def test_make_ansi_8bit():
    # Expected...
    e = "\x1b[53m\x1b[3m\x1b[48;5;3m\x1b[38;5;183m"
    # Created...
    f = ansy.make_ansi("plum", "yellow", ["italic", "overline"], 8)
    assert f == e

    with raises(InvalidColorError):
        ansy.make_ansi(bgcolor="asdf", color_mode=8)
    with raises(InvalidColorError):
        ansy.make_ansi(bgcolor=-5, color_mode=8)
    with raises(InvalidColorError):
        ansy.make_ansi(bgcolor=500, color_mode=8)


def test_make_ansi_24bit():
    # Expected...
    e = "\x1b[9m\x1b[8m\x1b[48;2;0;0;0m\x1b[38;2;255;100;100m"
    # Created...
    f = ansy.make_ansi((255, 100, 100), (0, 0, 0), ["concealed", "strike"], 24)
    assert f == e

    with raises(InvalidColorError):
        ansy.make_ansi(fgcolor="#asdf", color_mode=24)
    with raises(InvalidColorError):
        ansy.make_ansi(bgcolor=(255, 500, 500), color_mode=24)


def test_get_all_colors():
    # Type checking: Generator Expected
    assert isinstance(ansy.get_all_colors(), Generator)

    # Unsorted test
    for clr in ansy.get_all_colors():
        assert clr == ("black", 0)
        break

    # Sorted test
    for clr in ansy.get_all_colors(True):
        assert clr == ("aquamarine", 79)
        break


def test_de_ansi():
    # String to clean
    ansi_string = "\x1b[38;2;242;105;117mThis i\x1b[38;2;228;112;139ms an a\x1b[38;2;213;119;160mnsy te\x1b[38;2;198;126;182mst for\x1b[38;2;184;133;203m color\x1b[38;2;169;140;225ming an\x1b[38;2;154;147;246md stuf\x1b[38;2;150;150;254mf.\x1b[0m"
    clean = ansy.de_ansi(ansi_string)
    expected = "This is an ansy test for coloring and stuff."
    assert clean == expected

    with raises(TypeError):
        ansy.de_ansi(1234)

    with raises(TypeError):
        ansy.de_ansi(None)


def test_contains_ansi():
    dummy = "dummy string"
    assert not ansy.contains_ansi(ansy.colored(None))
    assert not ansy.contains_ansi(ansy.colored(""))
    assert not ansy.contains_ansi(ansy.colored(dummy))

    assert ansy.contains_ansi(
        ansy.colored(dummy, "red", "dark_grey", ["bold", "underline"], force_color=True)
    )
    assert ansy.contains_ansi(
        ansy.colored(
            dummy,
            "brown_sandy",
            "dark_grey",
            ["bold", "underline"],
            8,
            force_color=True,
        )
    )
    assert ansy.contains_ansi(
        ansy.colored(
            dummy, "#B00B1E", "#C0DDE5", ["bold", "underline"], 24, force_color=True
        )
    )

    with raises(TypeError):
        ansy.contains_ansi(None)
    with raises(TypeError):
        ansy.contains_ansi(123)


def test_make_gradient():
    grad = ansy.make_gradient((255, 100, 100), (50, 50, 100), 5, False)
    expected = [
        (255, 100, 100),
        (203, 87, 100),
        (152, 75, 100),
        (101, 62, 100),
        (50, 50, 100),
    ]

    # Colors checking
    grad_list = list(grad)
    assert len(grad_list) == len(expected)

    # Contents checking
    assert grad_list == expected

    with raises(InvalidColorError):
        list(ansy.make_gradient((1231, 123, 123), (123, 123, 123), 3))

    with raises(InvalidColorError):
        list(ansy.make_gradient((121, 123, 123), (123,), 3))

    with raises(InvalidColorError):
        list(ansy.make_gradient("fff", "#FFF123", 3))


def test_get_random_color():
    c4 = ansy.get_random_color(4)
    assert isinstance(c4, str)
    assert c4 in ansy.STANDARD_COLORNAMES

    c8 = ansy.get_random_color(8)
    assert isinstance(c8, str)
    assert c8 in ansy.COLORS256_COLORNAMES

    c24 = ansy.get_random_color(24)
    assert isinstance(c24, tuple)
    assert ansy.is_valid_rgb(c24) == True

    with raises(ColorModeError):
        ansy.get_random_color(245)


def test_create_style():
    e4 = {
        "color_mode": 4,
        "fgcolor": "light_red",
        "bgcolor": "dark_grey",
        "attrs": ["italic"],
    }
    s4 = ansy.create_style(4, "light_red", "dark_grey", ["italic"])

    assert s4 == e4

    # 8Bit checking
    e8 = {
        "color_mode": 8,
        "fgcolor": "smokewhite",
        "bgcolor": "plum",
        "attrs": ["bold", "underline"],
    }
    s8 = ansy.create_style(8, "smokewhite", "plum", ["bold", "underline"])

    assert s8 == e8

    # 24Bit checking
    e24 = {
        "color_mode": 24,
        "fgcolor": (255, 100, 100),
        "bgcolor": (0, 1, 0),
        "attrs": None,
    }
    s24 = ansy.create_style(24, (255, 100, 100), (0, 1, 0))

    assert s24 == e24

    with raises(InvalidColorError):
        ansy.create_style(8, "invcalid")

    with raises(InvalidColorError):
        ansy.create_style(4, (55, 100, 100), "123123")

    with raises(ColorModeError):
        ansy.create_style(2, (255, 100, 100), (0, 1, 0))

    with raises(AttributeError):
        ansy.create_style(24, (255, 100, 100), (0, 1, 0), ["boldd"])


def test_search_colors():
    expected = [
        ("plum", 183),
        ("plum_1", 176),
        ("plum_2", 219),
        ("plum_dim", 96),
        ("plum_dim_1", 139),
    ]

    result = ansy.search_colors("plum")

    assert isinstance(result, Generator)

    assert list(result) == expected


def test_hex_to_rgb():
    expected = (255, 242, 34)
    assert ansy.hex_to_rgb("#FFF222") == expected

    invalid_values = ["#FFF2", "$abc123", 123, None, 1.1, True, False]
    for v in invalid_values:
        with raises(HexError):
            ansy.hex_to_rgb(v)


def test_rgb_to_hex():
    expected = "#FFF222"
    assert ansy.rgb_to_hex((255, 242, 34)) == expected

    invalid_values = [
        ("123", "123", "12"),
        "('123','123', '12')",
        123,
        None,
        1.1,
        True,
        False,
    ]
    for v in invalid_values:
        with raises(RGBError):
            ansy.rgb_to_hex(v)


def test_colorname_to_code():
    assert ansy.colorname_to_code("plum") == ansy.COLORS_256["plum"]
    assert ansy.colorname_to_code(143) == 143
    assert ansy.colorname_to_code(None) == None

    # Raises no errors whatsoever!
    for v in ("asdf", 123, None, True, False, min, (12, 12), [123, 123], {"asd": 123}):
        ansy.colorname_to_code(v)


def test_code_to_colorname():
    assert ansy.code_to_colorname(ansy.COLORS_256["plum"]) == "plum"
    assert ansy.code_to_colorname("plum") == "plum"
    assert ansy.code_to_colorname(None) == None

    for v in ("asdf", 123, None, True, False, min):
        ansy.code_to_colorname(v)


# Tests for all validators


def test_is_valid_hex():
    # Valid Hex Checker
    valids = ["FFF", "#FFF", "fffFFF", "#FFFFFF"]
    for v in valids:
        assert ansy.is_valid_hex(v) == True

    invalids = ["#as", "#FFFFFz", None, 123]
    for v in invalids:
        assert ansy.is_valid_hex(v) == False


def test_is_valid_rgb():
    valids = [(200, 100, 1), (0, 0, 0), (255, 255, 255)]
    for v in valids:
        assert ansy.is_valid_rgb(v) == True

    invalids = [(), (255, 1), (-50, -5, 255), (500, 1000, 100), (None), (123), ("123")]
    for v in invalids:
        assert ansy.is_valid_rgb(v) == False


def test_is_valid_attr():
    # Valid Attr checker
    for attr in ("bold", "italic", "strike", "underline"):
        assert ansy.is_valid_attr(attr) == True

    # Invalid values
    for v in ("asd", 123, None, True, False):
        assert ansy.is_valid_attr(v) == False


def test_is_valid_color():
    valids = [
        ("yellow", 4),
        ("aquamarine", 8),
        ("yellow", 8),
        ("#fff", 24),
        ((255, 255, 100), 24),
    ]
    for v in valids:
        assert ansy.is_valid_color(*v) == True

    invalids = [
        ("aquamarine", 4),
        ("aquamarine", 24),
        ("yellow", 24),
        ("#fff", 4),
        ("#fff", 8),
        ("#safsaf", 4),
        ("#safsaf", 8),
        ("#safsaf", 24),
        ((255,), 4),
        ((255,), 8),
        ((255,), 24),
        ((255, 255, 100), 4),
        ((255, 255, 100), 8),
    ]
    for v in invalids:
        assert ansy.is_valid_color(*v) == False


if __name__ == "__main__":
    test_contains_ansi()
