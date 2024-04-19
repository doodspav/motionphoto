import struct

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from .exiftool import write_metadata_tags


class SamsungMarker(Enum):
    EmbeddedVideo = b"\x00\x00\x30\x0A"


@dataclass
class SamsungTag:
    offset: int
    marker: bytes


@dataclass
class SamsungTrailer:
    data: bytes
    negative_video_offset: int


def write_samsung_motion_metadata(*, media: Path, timestamp_us: Optional[int] = None) -> None:
    """
    Update existing media file with metadata required by Samsung's implementation of Motion Photos.

    :param media: Existing media file path.
    :param timestamp_us: Optional key-frame time offset in microseconds.

    :raise: RuntimeError: Calling 'exiftool' returned a non-zero exit code.
    """

    # metadata tags required by Samsung
    tags = [
        "-MotionPhoto=1",
        "-MotionPhotoVersion=1",
    ]
    if timestamp_us is not None:
        tags.append(f"-MotionPhotoPresentationTimestampUs={timestamp_us}")

    # write metadata tags
    write_metadata_tags(media=media, tags=tags)


def create_samsung_motion_trailer(*, video: Path) -> SamsungTrailer:
    """
    Create trailer data required by Samsung's implementation of Motion Photos that can be
    appended verbatim to an image file.

    :param video: Existing input video file path whose contents will be embedded in the trailer.
    :return: Raw trailer data in bytes, and byte offset from the end of the trailer to the
             start of the embedded video file.
    """

    # build up trailer
    trailer = bytearray()
    tags: [SamsungTag] = []

    # constants
    sef_version = struct.pack("<I", 106)

    # write EmbeddedVideoType
    tags.append(SamsungTag(offset=len(trailer), marker=SamsungMarker.EmbeddedVideo.value))
    trailer += SamsungMarker.EmbeddedVideo.value  # marker
    trailer += struct.pack("<I", 16)              # length
    trailer += b"MotionPhoto_Data"                # data

    # write EmbeddedVideoFile
    video_offset_positive = len(trailer)
    with open(video, 'rb') as f:
        trailer += f.read()

    # write SEF head
    tags.append(SamsungTag(offset=len(trailer), marker=b""))
    trailer += b"SEFH"               # head marker
    trailer += sef_version           # version
    trailer += struct.pack("<I", 1)  # field count

    # write info data for each tag (not including SEF)
    sef_offset: int = tags[-1].offset
    for i in range(len(tags) - 1):
        negative_offset_from_sef: int = sef_offset - tags[i].offset
        data_length: int = tags[i + 1].offset - tags[i].offset
        trailer += tags[i].marker
        trailer += struct.pack("<I", negative_offset_from_sef)  # negative offset from "SEFH"
        trailer += struct.pack("<I", data_length)               # distance from marker to next marker

    # write SEF tail
    sef_data_size: int = len(trailer) - sef_offset
    trailer += struct.pack("<I", sef_data_size)  # data size between SEFH and SEFT
    trailer += b"SEFT"                           # tail marker

    # return finished trailer
    video_offset_negative = len(trailer) - video_offset_positive
    return SamsungTrailer(data=bytes(trailer), negative_video_offset=video_offset_negative)
