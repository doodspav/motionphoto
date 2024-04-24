import os

from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, patch

from motionphoto.motion import (
    create_motion_photo,
    create_samsung_motion_trailer,
    write_google_motion_metadata,
    write_samsung_motion_metadata,
    SamsungTrailer,
)


class TestCreateMotionPhoto(TestCase):

    def setUp(self) -> None:

        # create required files
        with NamedTemporaryFile("r", prefix="MV", delete=False) as f:
            self.image_path = Path(f.name)
            self._image_path_to_delete = deepcopy(self.image_path)
        with NamedTemporaryFile("r", delete=False) as f:
            self.video_path = Path(f.name)
            self._video_path_to_delete = deepcopy(self.video_path)
        with NamedTemporaryFile("r", prefix="MV", delete=False) as f:
            self.motion_path = Path(f.name)
            self._motion_path_to_delete = deepcopy(self.motion_path)

        # check everything
        for p in [self.image_path, self.video_path, self.motion_path]:
            self.assertTrue(p.exists())

    def tearDown(self) -> None:

        # remove files we created
        os.remove(self._image_path_to_delete)
        os.remove(self._video_path_to_delete)
        for p in [self.image_path, self.video_path, self.motion_path]:
            if p.exists():  # pragma: no cover
                os.remove(p)  # pragma: no cover

    def test_image_not_exist(self) -> None:

        # setup
        self.image_path = Path("non_existent.jpeg")
        self.assertFalse(self.image_path.exists())

        # check
        with self.assertRaisesRegex(
            FileNotFoundError, f".*{self.image_path}.*"
        ):

            # test
            create_motion_photo(
                image=self.image_path,
                video=self.video_path,
                motion=self.motion_path,
            )

    def test_video_not_exist(self) -> None:

        # setup
        self.video_path = Path("non_existent.mov")
        self.assertFalse(self.video_path.exists())

        # check
        with self.assertRaisesRegex(
            FileNotFoundError, f".*{self.video_path}.*"
        ):

            # test
            create_motion_photo(
                image=self.image_path,
                video=self.video_path,
                motion=self.motion_path,
            )

    def test_motion_exists_no_overwrite(self) -> None:

        # check
        with self.assertRaisesRegex(FileExistsError, f".*{self.motion_path}.*"):

            # test
            create_motion_photo(
                image=self.image_path,
                video=self.video_path,
                motion=self.motion_path,
                overwrite=False,
            )

    def test_motion_bad_name(self) -> None:

        # setup
        self.motion_path = Path("not_mv.mov")

        # check
        with self.assertRaisesRegex(NameError, f".*{self.motion_path}.*"):

            # test
            create_motion_photo(
                image=self.image_path,
                video=self.video_path,
                motion=self.motion_path,
            )

    @patch("motionphoto.motion.write_google_motion_metadata")
    @patch("motionphoto.motion.write_samsung_motion_metadata")
    @patch("motionphoto.motion.create_samsung_motion_trailer")
    def test_motion_parent_dir_missing(
        self,
        mock_samsung_trailer: MagicMock,
        mock_samsung_metadata: MagicMock,
        mock_google_metadata: MagicMock,
    ) -> None:

        # setup
        with TemporaryDirectory() as temp_dir:
            self.motion_path = Path(temp_dir) / "non_existent" / "MV.jpeg"
            self.assertTrue(self.motion_path.parent.parent.exists())
            self.assertFalse(self.motion_path.parent.exists())
            self.assertFalse(self.motion_path.exists())
            data = b"hello"
            offset = 123
            timestamp = 456
            trailer = SamsungTrailer(data=data, negative_video_offset=offset)
            mock_samsung_trailer.return_value = trailer

            # test
            create_motion_photo(
                image=self.image_path,
                video=self.video_path,
                motion=self.motion_path,
                timestamp_us=timestamp,
                overwrite=False,
            )

            # check
            mock_samsung_trailer.assert_called_once_with(video=self.video_path)
            mock_samsung_metadata.assert_called_once_with(
                media=self.motion_path, timestamp_us=timestamp
            )
            mock_google_metadata.assert_called_once_with(
                media=self.motion_path,
                negative_video_offset=trailer.negative_video_offset,
                timestamp_us=timestamp,
            )
            self.assertTrue(self.motion_path.exists())
            with open(self.motion_path, "rb") as f:
                self.assertEqual(data, f.read())

    @patch("motionphoto.motion.write_google_motion_metadata")
    @patch("motionphoto.motion.write_samsung_motion_metadata")
    @patch("motionphoto.motion.create_samsung_motion_trailer")
    def test_motion_is_image_overwrite(
        self,
        mock_samsung_trailer: MagicMock,
        mock_samsung_metadata: MagicMock,
        mock_google_metadata: MagicMock,
    ) -> None:

        # setup
        with TemporaryDirectory() as temp_dir:
            self.motion_path = self.image_path
            existing_data = b"hello world"
            with open(self.image_path, "ab") as f:
                f.write(existing_data)
            data = b"hello"
            offset = 123
            timestamp = 456
            trailer = SamsungTrailer(data=data, negative_video_offset=offset)
            mock_samsung_trailer.return_value = trailer

            # test
            create_motion_photo(
                image=self.image_path,
                video=self.video_path,
                motion=self.motion_path,
                timestamp_us=timestamp,
                overwrite=True,
            )

            # check
            mock_samsung_trailer.assert_called_once_with(video=self.video_path)
            mock_samsung_metadata.assert_called_once_with(
                media=self.motion_path, timestamp_us=timestamp
            )
            mock_google_metadata.assert_called_once_with(
                media=self.motion_path,
                negative_video_offset=trailer.negative_video_offset,
                timestamp_us=timestamp,
            )
            self.assertTrue(self.motion_path.exists())
            with open(self.motion_path, "rb") as f:
                self.assertEqual(existing_data + data, f.read())
