from pathlib import Path
from typing import Optional

from .exiftool import write_metadata_tags


def write_google_motion_metadata(*, media: Path, negative_video_offset: int,
                                 timestamp_us: Optional[int] = None) -> None:
    """
    Update existing media file with metadata required by Google's implementation of Motion Photos.

    :param media: Existing media file path.
    :param negative_video_offset: Byte offset from end of media file to start of embedded video.
    :param timestamp_us: Optional key-frame time offset in microseconds.

    :raise: RuntimeError: Calling 'exiftool' returned a non-zero exit code.
    """

    # metadata tags required by Google
    tags = [
        "-MicroVideo=1",
        "-MicroVideoVersion=1",
        f"-MicroVideoOffset={negative_video_offset}",
        f"-MicroVideoPresentationTimestampUs={timestamp_us if timestamp_us is not None else -1}"
    ]

    # write metadata tags
    write_metadata_tags(media=media, tags=tags)
