import subprocess

from pathlib import Path


def write_google_motion_metadata(motion: Path, negative_video_offset: int, timestamp_us: int = -1) -> None:

    # exif tags required by Google
    tags = [
        "-MicroVideo=1",
        "-MicroVideoVersion=1",
        f"-MicroVideoOffset={negative_video_offset}",
        f"-MicroVideoPresentationTimestampUs={timestamp_us}"
    ]

    # write exif tags
    cmd = ["exiftool", "-overwrite_original", "-ignoreMinorErrors", *tags, str(motion)]
    res = subprocess.run(cmd, capture_output=True, text=True)

    # handle failure
    if res.returncode != 0:
        msg = f"Command '{' '.join(cmd)}' failed with error: {res.stderr}"
        raise RuntimeError(msg)
