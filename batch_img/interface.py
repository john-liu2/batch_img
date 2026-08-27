"""interface.py - define CLI interface
Copyright © 2025 John Liu
"""

import click
from loguru import logger as log

from batch_img.common import Common
from batch_img.const import MSG_BAD, MSG_OK, PKG_NAME
from batch_img.main import Main


def input_option(func):
    """Add the common input-source option to an image operation."""
    return click.option(
        "-i",
        "--input",
        "input_path",
        type=click.Path(path_type=str),
        help="Input image file or directory.",
    )(func)


def output_option(func):
    """Add the common output option to an image operation."""
    return click.option(
        "-o",
        "--output",
        default="",
        show_default=True,
        type=str,
        help="Output file path. If not specified, replace the input file.",
    )(func)


def common_cli_options(func):
    """Apply common options to all image operations."""
    func = input_option(func)
    func = output_option(func)
    return func


def process_result(result: bool) -> None:
    """Display the operation result message."""
    msg = MSG_OK if result else MSG_BAD
    click.secho(msg)


def get_input_path(
    ctx: click.Context, input_path: str | None, src_path: str | None
) -> str:
    """Resolve an operation's input source, including the legacy argument."""
    source = input_path or (ctx.obj or {}).get("input_path") or src_path
    if source:
        return source
    raise click.UsageError("Missing option '-i' / '--input'.", ctx)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(path_type=str),
    help="Input an image file or a directory.",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Process image files with minimum stdout in quiet mode.",
)
@click.option("--update", is_flag=True, help="Update the tool to the latest version.")
@click.option("--version", is_flag=True, help="Show the tool's version.")
def cli(  # noqa: PLR0913, PLR0917
    ctx, input_path, quiet, update, version
):
    """Batch image processing tool."""
    ctx.ensure_object(dict)
    ctx.obj["input_path"] = input_path
    ctx.obj["quiet"] = quiet

    if not ctx.invoked_subcommand:
        if update:
            Common.update_package(PKG_NAME)
        if version:
            click.secho(Common.get_version(PKG_NAME))
        if not update and not version:
            click.echo(ctx.get_help())


@cli.command(help="Print EXIF information for the input image file(s).")
@input_option
@click.pass_context
def info(ctx, input_path):
    """Print image file information."""
    source = get_input_path(ctx, input_path, None)
    quiet = (ctx.obj or {}).get("quiet", False) if ctx.obj else False
    Main.info({"src_path": source, "quiet": quiet})


@cli.command(
    help="Auto process (resize to 1920-px, remove GPS, add border) image file(s)."
)
@common_cli_options
@click.pass_context
@click.option(
    "-ar",
    "--auto_rotate",
    default=False,
    is_flag=True,
    show_default=True,
    help="Auto-rotate image (experimental)",
)
def auto(  # noqa: PLR0913, PLR0917
    ctx, input_path, output, auto_rotate
):
    source = get_input_path(ctx, input_path, None)
    options = {"src_path": source, "output": output, "auto_rotate": auto_rotate}
    if (ctx.obj or {}).get("quiet"):
        options["quiet"] = True
    process_result(Main.auto(options))


@cli.command(help="Add internal border to image file(s), not expand the size.")
@common_cli_options
@click.pass_context
@click.option(
    "-bw",
    "--border_width",
    default=5,
    show_default=True,
    type=click.IntRange(min=0, max=30),
    help="Add border to image file(s) with the border_width. 0 - no border.",
)
@click.option(
    "-bc",
    "--border_color",
    default="gray",
    show_default=True,
    help="Add border to image file(s) with the border_color string.",
)
def border(  # noqa: PLR0913, PLR0917
    ctx, input_path, output, border_width, border_color
):
    source = get_input_path(ctx, input_path, None)
    options = {
        "src_path": source,
        "output": output,
        "border_width": border_width,
        "border_color": border_color,
    }
    if (ctx.obj or {}).get("quiet"):
        options["quiet"] = True
    process_result(Main.border(options))


@cli.command(help="Do special effect to image file(s).")
@common_cli_options
@click.pass_context
@click.option(
    "-e",
    "--effect",
    is_flag=False,
    default="neon",
    show_default=True,
    type=click.Choice(["blur", "hdr", "neon"]),
    help="Do special effect to image file(s): blur, hdr, neon.",
)
def do_effect(  # noqa: PLR0913, PLR0917
    ctx, input_path, output, effect
):
    source = get_input_path(ctx, input_path, None)
    options = {"src_path": source, "output": output, "effect": effect}
    if (ctx.obj or {}).get("quiet"):
        options["quiet"] = True
    process_result(Main.do_effect(options))


@cli.command(help="Remove background (make background transparent) in image file(s).")
@common_cli_options
@click.pass_context
def remove_bg(  # noqa: PLR0913, PLR0917
    ctx, input_path, output
):
    log.info("Loading u2net.onnx to identify the background... Please be patient.")
    source = get_input_path(ctx, input_path, None)
    options = {"src_path": source, "output": output}
    if (ctx.obj or {}).get("quiet"):
        options["quiet"] = True
    process_result(Main.remove_bg(options))


@cli.command(help="Remove GPS location info in image file(s).")
@common_cli_options
@click.pass_context
def remove_gps(  # noqa: PLR0913, PLR0917
    ctx, input_path, output
):
    source = get_input_path(ctx, input_path, None)
    options = {"src_path": source, "output": output}
    if (ctx.obj or {}).get("quiet"):
        options["quiet"] = True
    process_result(Main.remove_gps(options))


@cli.command(help="Resize image file(s).")
@common_cli_options
@click.pass_context
@click.option(
    "-l",
    "--length",
    is_flag=False,
    default=0,
    show_default=True,
    type=click.IntRange(min=0),
    help="Resize image file(s) on original aspect ratio to"
    " the max side length. 0 - no resize.",
)
def resize(  # noqa: PLR0913, PLR0917
    ctx, input_path, output, length
):
    source = get_input_path(ctx, input_path, None)
    options = {"src_path": source, "output": output, "length": length}
    if (ctx.obj or {}).get("quiet"):
        options["quiet"] = True
    process_result(Main.resize(options))


@cli.command(help="Rotate image file(s).")
@common_cli_options
@click.pass_context
@click.option(
    "-a",
    "--angle",
    is_flag=False,
    default=0,
    show_default=True,
    type=click.Choice([0, 90, 180, 270]),
    help="Rotate image file(s) to the clockwise angle. 0 - no rotate.",
)
def rotate(  # noqa: PLR0913, PLR0917
    ctx, input_path, output, angle
):
    source = get_input_path(ctx, input_path, None)
    options = {
        "src_path": source,
        "output": output,
        "angle": angle,
    }
    if (ctx.obj or {}).get("quiet"):
        options["quiet"] = True
    process_result(Main.rotate(options))


@cli.command(help="Set transparency on image file(s).")
@common_cli_options
@click.pass_context
@click.option(
    "-t",
    "--transparency",
    is_flag=False,
    default=127,
    show_default=True,
    type=click.IntRange(min=0, max=255),
    help="Set transparency on image file(s)."
    " 0 - fully transparent, 255 - completely opaque.",
)
@click.option(
    "-w",
    "--white",
    is_flag=True,
    help="Make white pixels fully transparent.",
)
def transparent(  # noqa: PLR0913, PLR0917
    ctx, input_path, output, transparency, white
):
    source = get_input_path(ctx, input_path, None)
    options = {
        "src_path": source,
        "output": output,
        "transparency": transparency,
        "white": white,
    }
    if (ctx.obj or {}).get("quiet"):
        options["quiet"] = True
    process_result(Main.transparent(options))
