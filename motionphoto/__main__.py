import click

from pathlib import Path
from typing import Optional

from . import create_motion_photo
from . import __version__


# constants
CLI_PATH_FILE_RO = click.Path(exists=True, path_type=Path, readable=True, file_okay=True, dir_okay=False)
CLI_PATH_FILE_RW = click.Path(exists=True, path_type=Path, readable=True, writable=True, file_okay=True, dir_okay=False)


@click.command()
@click.version_option(__version__)
@click.option("-i", "--image", required=True, type=CLI_PATH_FILE_RO, help="Input image file path")
@click.option("-v", "--video", required=True, type=CLI_PATH_FILE_RO, help="Input video file path")
@click.option("-m", "--motion", required=True, type=CLI_PATH_FILE_RW, help="Output motion photo file path")
@click.option("-t_us", "--timestamp_us", type=int, help="Key-frame time offset in microseconds")
@click.option("--overwrite/--no-overwrite", default=False)
def cli_file(image: Path, video: Path, motion: Path, timestamp_us: Optional[int], overwrite: bool):
    create_motion_photo(image=image, video=video, motion=motion, timestamp_us=timestamp_us, overwrite=overwrite)


if __name__ == "__main__":
    cli_file()
