from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from motionphoto.motion import create_motion_photo


class TestCreateMotionPhoto(TestCase):

    def test_image_not_exist(self) -> None:
        pass

    def test_video_not_exist(self) -> None:
        pass

    def test_motion_exists_no_overwrite(self) -> None:
        pass

    def test_motion_bad_name(self) -> None:
        pass
    
    def test_motion_parent_dir_missing(self) -> None:
        pass

    def test_motion_is_image_overwrite(self) -> None:
        pass
