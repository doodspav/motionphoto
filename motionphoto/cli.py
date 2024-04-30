import mimetypes
import sys

from pathlib import Path
from typing import Optional

import click
import filetype

from .motion import create_motion_photo
from . import __version__


# helpers
CLI_PATH_FIN = click.Path(
    exists=True,
    path_type=Path,
    readable=True,
    writable=False,
    file_okay=True,
    dir_okay=False,
)
CLI_PATH_FOUT = click.Path(
    exists=False,
    path_type=Path,
    readable=True,
    writable=True,
    file_okay=True,
    dir_okay=False,
)


def validate_image_file(
    _ctx: click.Context, _param: click.Option, value: Path
) -> Path:
    """
    Check that file named by path has JPEG format.

    :param _ctx: Library context.
    :param _param: Command-line option parameter.
    :param value: Parameter value.
    :return: Validated parameter value.

    :raise click.BadParameter: File named by path is not JPEG.
    """

    # attempt to determine format
    guess = filetype.guess(value)
    mime: Optional[str] = (
        guess.mime if guess is not None else mimetypes.guess_type(value)[0]
    )

    # check that format is JPEG
    if mime not in ("image/jpeg", "image/jpg"):  # second is non-standard
        raise click.BadParameter("Input image file format must be JPEG")

    # success
    return value


def validate_video_file(
    _ctx: click.Context, _param: click.Option, value: Path
) -> Path:
    """
    Check that file named by path is not bigger than ``INT32_MAX`` bytes.

    :param _ctx: Library context.
    :param _param: Command-line option parameter.
    :param value: Parameter value.
    :return: Validated parameter value.

    :raise click.BadParameter: File named by path exceeds ``INT32_MAX`` bytes.
    """

    # check that file size fits in signed 32bit integer
    # if it's bigger, we may not be able to write file offset in metadata
    if value.stat().st_size > 2**31 - 1:
        raise click.BadParameter(
            f"Input video file size cannot exceed {2 ** 31 - 1} bytes"
        )

    # success
    return value


def validate_motion_file(
    _ctx: click.Context, _param: click.Option, value: Path
) -> Path:
    """
    Check that file name from path starts with ``'MV'``.

    :param _ctx: Library context.
    :param _param: Command-line option parameter.
    :param value: Parameter value.
    :return: Validated parameter value.

    :raise click.BadParameter: File name from path does not start with ``'MV'``.
    """

    # check that file name starts with 'MV'
    if not value.name.startswith("MV"):
        raise click.BadParameter(
            "Motion Photo names must start with 'MV' to be playable "
            "in Google Gallery"
        )

    # success
    return value


@click.command()
@click.version_option(__version__)
@click.option(
    "-i",
    "--image",
    required=True,
    type=CLI_PATH_FIN,
    callback=validate_image_file,
    help="Input image file path (format must be JPEG)",
)
@click.option(
    "-v",
    "--video",
    required=True,
    type=CLI_PATH_FIN,
    callback=validate_video_file,
    help="Input video file path",
)
@click.option(
    "-m",
    "--motion",
    required=True,
    type=CLI_PATH_FOUT,
    callback=validate_motion_file,
    help="Output motion photo file path (name must start with 'MV')",
)
@click.option(
    "-t_us",
    "--timestamp_us",
    type=click.IntRange(min=0),
    help="Key-frame time offset in microseconds "
    "(may be derived from image/video inputs if omitted)",
)
@click.option(
    "--overwrite/--no-overwrite",
    default=False,
    help="Overwrite existing motion photo file instead of returning an error",
)
def cli_file(
    image: Path,
    video: Path,
    motion: Path,
    timestamp_us: Optional[int],
    overwrite: bool,
) -> None:
    """Handle command line usage of motionphoto."""

    # create motion photo
    try:
        create_motion_photo(
            image=image,
            video=video,
            motion=motion,
            timestamp_us=timestamp_us,
            overwrite=overwrite,
        )

    # specifically catch this error to provide helpful tip about --overwrite
    except FileExistsError:
        click.echo(
            f"Error: Output motion photo file already exists: {motion} "
            "(try using --overwrite)",
            err=True,
        )
        sys.exit(1)

    # allow all other exceptions to propagate to caller
    # so that they can see the stack trace
