"""interface.py - define CLI interface
Copyright © 2025 John Liu
"""

import click

from batch_img.common import Common
from batch_img.const import MSG_BAD, MSG_OK
from batch_img.main import Main


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--version", is_flag=True, help="Show this tool's version")
def cli(ctx, version):  # pragma: no cover
    if not ctx.invoked_subcommand:
        if version:
            click.secho(Common.get_version())


@cli.command(help="Add border to image file(s)")
@click.argument(
    "src_path",
    required=True,
)
@click.option(
    "-bw",
    "--border_width",
    default=5,
    show_default=True,
    help="Add border to image file(s) with the border_width. 0 - no border",
)
@click.option(
    "-bc",
    "--border_color",
    default="gray",
    show_default=True,
    help="Add border to image file(s) with the border_color string",
)
def border(src_path, border_width, border_color):
    options = {
        "src_path": src_path,
        "border_width": border_width,
        "border_color": border_color,
    }
    res = Main.add_border(options)
    msg = MSG_OK if res else MSG_BAD
    click.secho(msg)


@cli.command(
    help="Process image file(s) with default actions:\n"
    "1) resize to 1280; 2) add 5-pixel gray color border; 3) no rotate"
)
@click.argument(
    "src_path",
    required=True,
)
def defaults(src_path):
    """Do the default action on the image file(s):
    * Resize to 1280 pixels as the max width
    * Add a border: 5 pixel width, gray color
    * No rotate
    """
    options = {
        "src_path": src_path,
    }
    res = Main.default_run(options)
    msg = MSG_OK if res else MSG_BAD
    click.secho(msg)


@cli.command(help="Resize image file(s)")
@click.argument(
    "src_path",
    required=True,
)
@click.option(
    "-w",
    "--width",
    is_flag=False,
    default=0,
    show_default=True,
    type=int,
    help="Resize image file(s) on current aspect ratio to the width. 0 - no resize",
)
def resize(src_path, width):
    options = {
        "src_path": src_path,
        "width": width,
    }
    res = Main.resize(options)
    msg = MSG_OK if res else MSG_BAD
    click.secho(msg)


@cli.command(help="Rotate image file(s)")
@click.argument(
    "src_path",
    required=True,
)
@click.option(
    "-d",
    "--degree",
    is_flag=False,
    default=0,
    show_default=True,
    type=int,
    help="Rotate image file(s) to the degree clock-wise. 0 - no rotate",
)
def rotate(src_path, degree):
    options = {
        "src_path": src_path,
        "degree": degree,
    }
    res = Main.rotate(options)
    msg = MSG_OK if res else MSG_BAD
    click.secho(msg)
