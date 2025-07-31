"""
Simple Helper Module to provide widely used colors. 

These Colors Include:
- `19` Material Colors (with `14` different shades in each)
- `140` Web/HTML Colors
- `200` Individual Color Palettes (with `5` colors in each)
"""

from . import _corpus_colors
from random import choice
from typing import List, Dict


def get_web_colors():
    """
    ### Get Web Colors
    Yields Web/HTML colors in `dict`.
    ```
    #### dict Structure:
    {
        'color':"AliceBlue",
        'hex':"#F0F8FF"
    }
    ```
    """
    for color in _corpus_colors.web_colors:
        yield color


def get_palettes():
    """
    ### Get Palettes
    Yields a palette per `list`.
    ```
    #### List Structure:
    [
        "#69D2E7",
        "#A7DBD8",
        "#E0E4CC",
        "#F38630",
        "#FA6900"
    ]
    ```
    """
    for palette in _corpus_colors.palettes:
        yield palette


def get_random_palette() -> List[str]:
    """
    ### Get Random Palette
    Returns a random color palette.
    """
    return choice(_corpus_colors.palettes)


def get_material_color(color: _corpus_colors.MaterialColor) -> Dict:
    """
    ### Get Material Colors
    Returns a `dict` of a material `color` (all of its shades).

    #### Material Colors:
    Google's Material Colors include `red`, `pink`, `purple`, `deeppurple`, `indigo`,
    `blue`, `lightblue`, `cyan`, `teal`, `green`, `lightgreen`, `lime`, `yellow`,
    `amber`, `orange`, `deeporange`, `brown`, `grey`, `bluegrey`.

    Shades of each color: `50`, `100`, `200`, `300`, `400`, `500`, `600`, `700`, `800`,
    `900`, `a100`, `a200`, `a400`, `a700`.
    ```
    #### dict Structure:
    {
        "50": "#ffebee",
        "100": "#ffcdd2",
        ...,
        "a700": "#d50000"
    }
    ```
    """
    return _corpus_colors.material_colors.get(color, None)
