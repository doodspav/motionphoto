from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional
from unittest import TestCase

import motionphoto
from tests.integration import helpers


class TestMotionPhotoApi(TestCase):

    def get_image_paths(self) -> List[Path]:

        # build up paths
        data_path = Path(__file__).parent / "data"
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
                motionphoto.create_motion_photo(
                    image=image_path,
                    video=video_path,
                    motion=motion_path,
                )

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
                motionphoto.create_motion_photo(
                    image=image_path,
                    video=video_path,
                    motion=motion_path,
                    timestamp_us=i,
                )

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
                motionphoto.create_motion_photo(
                    image=image_path,
                    video=video_path,
                    motion=motion_path,
                )

                # check
                self.assert_motion(
                    motion_path=motion_path,
                    video_data=video_data,
                    timestamp_us=None,
                )
