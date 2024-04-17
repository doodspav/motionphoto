from pathlib import Path

from .exiftool import write_metadata_tags


def write_google_motion_metadata(*, motion: Path, negative_video_offset: int, timestamp_us: int = -1) -> None:

    # metadata tags required by Google
    tags = [
        "-MicroVideo=1",
        "-MicroVideoVersion=1",
        f"-MicroVideoOffset={negative_video_offset}",
        f"-MicroVideoPresentationTimestampUs={timestamp_us}"
    ]

    # write metadata tags
    write_metadata_tags(media=motion, tags=tags)
