from pathlib import Path
from typing import Optional

from .exiftool import write_metadata_tags


def write_google_motion_metadata(*, motion: Path, negative_video_offset: int,
                                 timestamp_us: Optional[int] = None) -> None:
    """
    Write metadata required by Google's implementation of Motion Photos to file.

    :param motion: Existing Motion Photo file path.
    :param negative_video_offset: Byte offset from end of file to start of embedded video.
    :param timestamp_us: Optional key-frame time offset in microseconds.
    """

    # metadata tags required by Google
    tags = [
        "-MicroVideo=1",
        "-MicroVideoVersion=1",
        f"-MicroVideoOffset={negative_video_offset}",
        f"-MicroVideoPresentationTimestampUs={timestamp_us if timestamp_us is not None else -1}"
    ]

    # write metadata tags
    write_metadata_tags(media=motion, tags=tags)
