"""CLI interface"""

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


@cli.command(
    help="The image file path or the folder path containing multiple image files"
)
@click.argument(
    "src_path",
    required=True,
)
@click.option(
    "--add_border",
    nargs=2,
    default=(5, "gray"),
    show_default=True,
    type=(int, str),
    help="Add border to the image file(s) with (border_width, border_color)."
    " Default is (5 'gray')",
)
@click.option(
    "--resize",
    is_flag=False,
    default=0,
    show_default=True,
    type=int,
    help="Resize the image file(s) on current aspect ratio to the width."
    " Default 0 - no resize",
)
@click.option(
    "--rotate",
    is_flag=False,
    default=0,
    show_default=True,
    type=int,
    help="Rotate the image file(s) to the given degree clock-wise."
    " Default 0 - no rotate",
)
def action(src_path, add_border, resize, rotate):
    options = {
        "src_path": src_path,
        "add_border": add_border,
        "resize": resize,
        "rotate": rotate,
    }
    ret = Main.run(options)
    if ret:
        click.secho(MSG_OK, fg="green")
    else:
        click.secho(MSG_BAD)
