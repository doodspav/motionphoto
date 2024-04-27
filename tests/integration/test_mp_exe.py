import os
import subprocess
import sys

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional
from unittest import TestCase

from . import helpers


class TestMotionPhotoExecutable(TestCase):

    def get_env(self) -> Dict[str, str]:

        # updated environment variables with PYTHONPATH giving our module
        environ = dict(os.environ)
        if "PYTHONPATH" not in environ:  # pragma: no cover
            environ["PYTHONPATH"] = ""  # pragma: no cover
        mod_path = Path(__file__).parent.parent.parent
        environ["PYTHONPATH"] = f"{mod_path}{os.pathsep}{environ['PYTHONPATH']}"
        return environ

    def get_image_paths(self) -> List[Path]:

        # build up paths
        data_path = Path(__file__).parent.parent / "data"
        jpeg_suffixes = (".jpeg", ".jpg")
        image_paths = [
            p for p in data_path.iterdir() if p.suffix.lower() in jpeg_suffixes
        ]
        return image_paths

    def assert_motion(
        self,
        *,
        motion_path: Path,
        video_data: bytes,
        timestamp_us: Optional[int],
    ) -> None:

        # defer to helper
        helpers.assert_motion(
            self,
            motion_path=motion_path,
            video_data=video_data,
            timestamp_us=timestamp_us,
        )

    def test_jpeg(self) -> None:

        # setup
        image_paths = self.get_image_paths()
        with TemporaryDirectory() as temp_dir:
            video_data = b"video abcdefg"
            video_path = Path(temp_dir) / "video.mov"
            with open(video_path, "wb") as f:
                f.write(video_data)

            # test
            for i, image_path in enumerate(image_paths):
                motion_path = Path(temp_dir) / f"MV_{i}.jpeg"
                cmd = [
                    # fmt: off
                    sys.executable, "-m", "motionphoto",
                    "-i", f"{image_path}",
                    "-v", f"{video_path}",
                    "-m", f"{motion_path}",
                    # fmt: on
                ]
                res = subprocess.run(cmd, env=self.get_env(), check=True)

                # check
                self.assert_motion(
                    motion_path=motion_path,
                    video_data=video_data,
                    timestamp_us=None,
                )

    def test_jpeg_with_timestamp(self) -> None:

        # setup
        image_paths = self.get_image_paths()
        with TemporaryDirectory() as temp_dir:
            video_data = b"video abcdefg"
            video_path = Path(temp_dir) / "video.mov"
            with open(video_path, "wb") as f:
                f.write(video_data)

            # test
            for i, image_path in enumerate(image_paths):
                motion_path = Path(temp_dir) / f"MV_{i}.jpeg"
                cmd = [
                    # fmt: off
                    sys.executable, "-m", "motionphoto",
                    "-i", f"{image_path}",
                    "-v", f"{video_path}",
                    "-m", f"{motion_path}",
                    "-t_us", f"{i}"
                    # fmt: on
                ]
                res = subprocess.run(cmd, env=self.get_env(), check=True)

                # check
                self.assert_motion(
                    motion_path=motion_path,
                    video_data=video_data,
                    timestamp_us=i,
                )

    def test_jpeg_empty_video(self) -> None:

        # setup
        image_paths = self.get_image_paths()
        with TemporaryDirectory() as temp_dir:
            video_data = b""
            video_path = Path(temp_dir) / "empty_video.mov"
            with open(video_path, "wb") as f:
                f.write(video_data)

            # test
            for i, image_path in enumerate(image_paths):
                motion_path = Path(temp_dir) / f"MV_{i}.jpeg"
                cmd = [
                    # fmt: off
                    sys.executable, "-m", "motionphoto",
                    "-i", f"{image_path}",
                    "-v", f"{video_path}",
                    "-m", f"{motion_path}",
                    # fmt: on
                ]
                res = subprocess.run(cmd, env=self.get_env(), check=True)

                # check
                self.assert_motion(
                    motion_path=motion_path,
                    video_data=video_data,
                    timestamp_us=None,
                )
