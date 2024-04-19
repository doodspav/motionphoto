import shutil

from pathlib import Path
from typing import Optional

from .samsung import SamsungTrailer
from .samsung import create_samsung_motion_trailer, write_samsung_motion_metadata
from .google import write_google_motion_metadata


def create_motion_photo(*, image: Path, video: Path, motion: Path,
                        timestamp_us: Optional[int] = None, overwrite: bool = False) -> None:
    """
    Create a Motion Photo from an input image and video.

    If no timestamp_us is passed, this function will attempt to determine the correct
    value from the metadata in the image and video files. If no timestamp can be determined,
    then it will fall back to an empty default.

    :param image: Existing input image file path, format should support exif data.
    :param video: Existing input video file path.
    :param motion: Output file path where Motion Photo will be created or overwritten.
    :param timestamp_us: Optional key-frame time offset in microseconds.
    :param overwrite: Overwrite existing file (otherwise raise an exception).
    """

    # check input files exist
    if not image.exists():
        raise RuntimeError(f"Input image file does not exist: {image}")
    if not video.exists():
        raise RuntimeError(f"Input video file does not exist: {video}")

    # check if output file exists
    if motion.exists() and not overwrite:
        raise RuntimeError(f"Output motion photo file already exists: {motion}")

    # check motion file name starts with MV
    # required for proper playback in Google Gallery app
    if not motion.name.startswith("MV"):
        raise RuntimeError(f"Motion Photo name must start with 'MV' for Google Gallery playback, path: {motion}")

    # create output file from image
    if not motion.parent.exists():
        motion.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(image, motion)

    # write trailer data required by Samsung
    samsung_trailer: SamsungTrailer = create_samsung_motion_trailer(video=video)
    with open(motion, 'ab') as f:
        f.write(samsung_trailer.data)

    # write metadata required by Samsung and Google
    write_samsung_motion_metadata(motion=motion, timestamp_us=timestamp_us)
    write_google_motion_metadata(motion=motion, negative_video_offset=samsung_trailer.negative_video_offset,
                                 timestamp_us=timestamp_us)
