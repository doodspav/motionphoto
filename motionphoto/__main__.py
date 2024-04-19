import click
import sys

from pathlib import Path
from typing import Optional

from . import create_motion_photo
from . import __version__


# helpers
CLI_PATH_FIN = click.Path(exists=True, path_type=Path, readable=True, file_okay=True, dir_okay=False)
CLI_PATH_FOUT = click.Path(exists=False, path_type=Path, readable=True, writable=True, file_okay=True, dir_okay=False)


def validate_motion_path(_ctx, _param, value: Path) -> Path:
    if not value.name.startswith("MV"):
        raise click.BadParameter("Motion Photo names must start with 'MV' to be playable in Google Gallery")
    return value


@click.command()
@click.version_option(__version__)
@click.option("-i", "--image", required=True, type=CLI_PATH_FIN, help="Input image file path")
@click.option("-v", "--video", required=True, type=CLI_PATH_FIN, help="Input video file path")
@click.option("-m", "--motion", required=True, type=CLI_PATH_FOUT, callback=validate_motion_path,
              help="Output motion photo file path (name must start with 'MV')")
@click.option("-t_us", "--timestamp_us", type=int,
              help="Key-frame time offset in microseconds (may be derived from image/video inputs if omitted)")
@click.option("--overwrite/--no-overwrite", default=False)
def cli_file(image: Path, video: Path, motion: Path, timestamp_us: Optional[int], overwrite: bool):

    # check if motion file exists here, to give a better error message
    if motion.exists() and not overwrite:
        print(f"Error: Output motion photo file already exists: '{motion}' (try using --overwrite)")
        exit(1)

    # create motion photo
    try:
        create_motion_photo(image=image, video=video, motion=motion, timestamp_us=timestamp_us, overwrite=overwrite)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr, flush=True)
        exit(1)


if __name__ == "__main__":
    cli_file()
