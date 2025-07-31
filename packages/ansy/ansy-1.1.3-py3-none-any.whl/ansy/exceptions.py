""" All Exceptions used by `Ansy` """


class StyleError(Exception):
    """Invalid style for `Ansy strings`"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.args = args


class ColorModeError(Exception):
    """Inappropriate color mode that is unrecognized by `Ansy`"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.args = args


class InvalidColorError(Exception):
    """Inappropriate color that is unrecognized by `Ansy`"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.args = args


class RGBError(InvalidColorError):
    """Invalid RGB"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.args = args


class HexError(InvalidColorError):
    """Invalid Hex color code"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.args = args
