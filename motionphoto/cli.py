import mimetypes
import shutil
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import click
import filetype
import tqdm

from .motion import create_motion_photo
from . import __version__


@dataclass
class ImageVideoPair:
    """
    Helper type representing an image-video file pair to be turned into a
    Motion Photo.

    :ivar Path image: Path to image file to be used as base of Motion Photo.
    :ivar Path video: Path to video file to be included into Motion Photo.
    """

    image: Path
    video: Path


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
CLI_PATH_DIN = click.Path(
    exists=True,
    path_type=Path,
    readable=True,
    writable=False,
    file_okay=False,
    dir_okay=True,
)
CLI_PATH_DOUT = click.Path(
    exists=False,
    path_type=Path,
    readable=True,
    writable=True,
    file_okay=False,
    dir_okay=True,
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


def split_input_directory(
    *,
    input_dir: Path,
) -> Tuple[List[ImageVideoPair], List[Path]]:
    """
    Attempt to pair up all images file with a correspondingly named video file
    in a directory, and separate these pairs from all other files in a given
    input directory.

    Files will be paired if there exist an image and video file with the same
    stem (a.k.a. the same name not including the file extension).

    :param input_dir: Existing directory containing files to split.
    :return: List of paired files and list of unpaired files.

    :raise: FileNotFoundError: The input_dir does not exist.
    :raise: RuntimeError: The input_dir is not a directory.
    """

    # check inpu_dir exists and is a directory
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    elif not input_dir.is_dir():
        raise RuntimeError(
            f"Input directory exists and is not a directory: {input_dir}"
        )

    # set up containers
    image_files: Dict[str, str] = {}  # dict: stem -> suffix
    video_files: Dict[str, str] = {}  # dict: stem -> suffix
    other_files: [Path] = []  # list: path

    # parse all files in directory into containers
    for file in input_dir.iterdir():
        if file.is_file():

            # attempt to determine format
            guess = filetype.guess(file)
            mime: Optional[str] = (
                guess.mime
                if guess is not None
                else mimetypes.guess_type(file)[0]
            )

            # place file in appropriate container
            if mime is None:
                other_files.append(file)
            elif mime.startswith("image/"):
                image_files[file.stem] = file.suffix
            elif mime.startswith("video/"):
                video_files[file.stem] = file.suffix
            else:
                other_files.append(file)

    # process files into image-video pairs
    iv_pairs: List[ImageVideoPair] = []
    for image_stem, image_suffix in image_files.items():
        if image_stem in video_files:
            iv_pairs.append(
                ImageVideoPair(
                    image=input_dir / f"{image_stem}{image_suffix}",
                    video=input_dir / f"{image_stem}{video_files[image_stem]}",
                )
            )

    # remove used stems
    used_stems: List[str] = [iv.image.stem for iv in iv_pairs]
    for stem in used_stems:
        del image_files[stem]
        del video_files[stem]

    # deal with remaining files
    for image_stem, image_suffix in image_files.items():
        other_files.append(input_dir / f"{image_stem}{image_suffix}")
    for video_stem, video_suffix in video_files.items():
        other_files.append(input_dir / f"{video_stem}{video_suffix}")

    # finished
    return iv_pairs, other_files


def populate_output_directory(
    *,
    iv_pairs: List[ImageVideoPair],
    other_files: Optional[List[Path]],
    output_dir: Path,
    overwrite: bool = False,
    progress: bool = False,
) -> None:
    """
    Convert all image-video pairs into Motion Photos in the output directory,
    and conditionally also copy all other files into the output directory as
    well.

    :param iv_pairs: Image-video pairs to be converted into Motion Photos.
    :param other_files: Non-paired files, which may be copied verbatim.
    :param output_dir: Directory into which to write files.
    :param overwrite: Overwrite existing files instead of raising an exception.
    :param progress: Display a dynamically updating progress bar.

    :raise: RuntimeError: The output_dir is not a directory.
    :raise: FileExistsError: One or more files would be overwritten.
    """

    # make sure output directory exists
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    elif not output_dir.is_dir():
        raise RuntimeError(
            f"Output directory exists and is not a directory: {output_dir}"
        )

    # check if any new files would overwrite existing files
    if not overwrite:
        existing_files: Set[str] = {p.name for p in output_dir.iterdir()}
        new_files: Set[str] = (
            set(other_files) if other_files is not None else set()
        )
        for iv in iv_pairs:
            new_files.add(f"MV{iv.image.name}")
        overwritten_files: Set[str] = existing_files.intersection(new_files)
        if overwritten_files:
            raise FileExistsError(
                "The following files would be overwritten (use --overwrite): "
                f"{overwritten_files}"
            )

    # covert all image-video pairs to Motion Photos
    iter_iv_pairs = (
        tqdm.tqdm(iv_pairs, desc="Processing Motion Photos", unit=" photos")
        if progress
        else iv_pairs
    )
    for iv in iter_iv_pairs:
        motion: Path = output_dir / f"MV{iv.image.name}"
        create_motion_photo(
            image=iv.image, video=iv.image, motion=motion, overwrite=overwrite
        )

    # copy other files
    if other_files is not None:
        iter_other_files = (
            tqdm.tqdm(other_files, desc="Copying other files", unit=" files")
            if progress
            else other_files
        )
        for file in iter_other_files:
            shutil.copy(file, output_dir)


@click.command()
@click.version_option(__version__)
@click.option(
    "-i",
    "--input-dir",
    required=True,
    type=CLI_PATH_DIN,
    help="Input directory path, containing image and video files",
)
@click.option(
    "-o",
    "--output-dir",
    required=True,
    type=CLI_PATH_DOUT,
    help="Output directory path, to write motion photo files into",
)
@click.option(
    "--copy-other/--no-copy-other",
    default=True,
    help="Copy files that will not become Motion Photos to the output directory",
)
@click.option(
    "--overwrite/--no-overwrite",
    default=False,
    help="Overwrite existing motion photo file instead of returning an error",
)
@click.option(
    "--progress/--no-progress",
    default=True,
    help="Display a dynamically updated progress bar",
)
def cli_dir(
    input_dir: Path,
    output_dir: Path,
    copy_other: bool,
    overwrite: bool,
    progress: bool,
) -> None:
    """Handle command line usage of motionphotodir."""

    # split input
    split_dir: Tuple[List[ImageVideoPair], List[Path]] = split_input_directory(
        input_dir=input_dir
    )
    other_files_opt: Optional[List[Path]] = split_dir[1] if copy_other else None

    # create output
    populate_output_directory(
        iv_pairs=split_dir[0],
        other_files=other_files_opt,
        output_dir=output_dir,
        overwrite=overwrite,
        progress=progress,
    )
