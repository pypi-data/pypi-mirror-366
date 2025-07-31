import ansy
from argparse import ArgumentParser


def main():
    args = get_args()

    text = args.text
    fgcolor = args.fgcolor
    bgcolor = args.bgcolor
    color_mode = args.mode

    if color_mode and color_mode not in (4, 8, 24):
        error(f"Invalid color mode: {color_mode}, must be 4, 8, or 24.")

    if fgcolor:
        if not ansy.is_valid_color(fgcolor, color_mode):
            error(f"Invalid foreground color: {fgcolor}")
    else:
        fgcolor = ansy.get_random_color(color_mode)

    if bgcolor and not ansy.is_valid_color(bgcolor, color_mode):
        error(f"Invalid background color: {bgcolor}")

    ansy.printc(text, fgcolor, bgcolor, color_mode=color_mode)


def get_args():
    parser = ArgumentParser(
        usage="ansy [OPTIONS]",
        description="Command-line utility to color text.",
        epilog="ansy v1.1.3",
    )

    parser.add_argument(
        "-t", "--text", help="the text to color", metavar="", default="Welcome to ansy."
    )
    parser.add_argument(
        "-fg", "--fgcolor", help="the foreground color of text", metavar=""
    )
    parser.add_argument(
        "-bg", "--bgcolor", help="the background color of text", metavar=""
    )
    parser.add_argument(
        "-m",
        "--mode",
        help="the color mode (4, 8, or 24)",
        metavar="",
        type=int,
        default=4,
    )

    # Parse and return Args
    return parser.parse_args()


def error(message):
    ansy.printc(f"Error: {message}", fgcolor="light_red")
    exit(1)
