import json
import subprocess

from pathlib import Path
from typing import Optional
from unittest import TestCase


def check_motion(
    self: TestCase,
    *,
    motion_path: Path,
    video_data: bytes,
    timestamp_us: Optional[int],
) -> None:

    # setup
    known_fields = {
        "SourceFile": f"{motion_path}",
        "MicroVideo": 1,
        "MicroVideoVersion": 1,
        "MicroVideoPresentationTimestampUs": (
            -1 if timestamp_us is None else timestamp_us
        ),
        "MotionPhoto": 1,
        "MotionPhotoVersion": 1,
        "EmbeddedVideoType": "MotionPhoto_Data",
        "EmbeddedVideoFile": video_data.decode("utf-8"),
    }
    unknown_fields = [
        "MicroVideoOffset",
        "MotionPhotoPresentationTimestampUs",
    ]

    # invoke exiftool
    config_path = (
        Path(__file__).parent.parent.parent
        / "motionphoto"
        / "exiftool.config.pl"
    )
    cmd = ["exiftool", "-config", f"{config_path}", "-j", "-b"]
    cmd += [f"-{f}" for f in list(known_fields.keys()) + unknown_fields]
    cmd += [f"{motion_path}"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # check
    self.assertEqual(0, res.returncode)
    self.assertTrue(motion_path.exists())
    output = json.loads(res.stdout)[0]
    for k, v in known_fields.items():
        self.assertIn(k, output)
        self.assertEqual(known_fields[k], output[k])
    self.assertIn("MicroVideoOffset", output)
    with open(motion_path, "rb") as f:
        file_data = f.read()
        negative_offset = len(file_data) - file_data.find(video_data)
        self.assertEqual(negative_offset, output["MicroVideoOffset"])
    if timestamp_us is not None:
        self.assertIn("MotionPhotoPresentationTimestampUs", output)
        self.assertEqual(
            timestamp_us, output["MotionPhotoPresentationTimestampUs"]
        )
    else:
        self.assertNotIn("MotionPhotoPresentationTimestampUs", output)