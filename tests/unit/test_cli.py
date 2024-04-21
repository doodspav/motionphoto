from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click import Context, Option, BadParameter
from click.testing import CliRunner

from motionphoto.cli import (
    cli_file,
    validate_image_file,
    validate_motion_file,
    validate_video_file,
)


class ValidateParamTestCase(TestCase):

    def setUp(self) -> None:
        self.unused_ctx = MagicMock(spec=Context)
        self.unused_param = MagicMock(spec=Option)

    def tearDown(self) -> None:
        self.unused_ctx.assert_not_called()
        self.unused_param.assert_not_called()


class TestValidateImageFile(ValidateParamTestCase):

    JPEG_MAGIC: bytes = b"\xFF\xD8\xFF\xE0"

    def test_bad_filetype_bad_mimetypes(self) -> None:

        # setup
        with NamedTemporaryFile(mode="r", suffix=".not_jpeg") as f:
            path = Path(f.name)

            # check
            with self.assertRaises(BadParameter):

                # test
                validate_image_file(self.unused_ctx, self.unused_param, path)

    def test_good_filetype_bad_mimetype(self) -> None:

        # setup
        with NamedTemporaryFile(mode="rb+", suffix=".not_jpeg") as f:
            path = Path(f.name)
            f.write(TestValidateImageFile.JPEG_MAGIC)
            f.flush()

            # test
            res = validate_image_file(self.unused_ctx, self.unused_param, path)

            # check
            self.assertEqual(res, path)

    def test_bad_filetype_good_mimetypes(self) -> None:

        # setup
        for suffix in [".jpeg", ".jpg"]:
            with NamedTemporaryFile(mode="r", suffix=suffix) as f:
                path = Path(f.name)

                # test
                res = validate_image_file(
                    self.unused_ctx, self.unused_param, path
                )

                # check
                self.assertEqual(res, path)

    def test_good_filetype_good_mimetypes(self) -> None:

        # setup
        for suffix in [".jpeg", ".jpg"]:
            with NamedTemporaryFile(mode="rb+", suffix=suffix) as f:
                path = Path(f.name)
                f.write(TestValidateImageFile.JPEG_MAGIC)
                f.flush()

                # test
                res = validate_image_file(
                    self.unused_ctx, self.unused_param, path
                )

                # check
                self.assertEqual(res, path)


class TestValidateVideoFile(ValidateParamTestCase):

    MAX_SZE: int = 2**31 - 1

    @patch("pathlib.Path.stat")
    def test_size_too_large(self, mock_stat: MagicMock) -> None:

        # setup
        mock_stat.return_value.st_size = TestValidateVideoFile.MAX_SZE + 1
        path = Path()

        # check
        with self.assertRaises(BadParameter):

            # test
            validate_video_file(self.unused_ctx, self.unused_param, path)

        # check
        mock_stat.assert_called_once()

    @patch("pathlib.Path.stat")
    def test_size_good(self, mock_stat: MagicMock) -> None:

        # setup
        # fmt: off
        valid_sizes = [
            -200, -1, 0, 1, 200,
            -2 * TestValidateVideoFile.MAX_SZE, TestValidateVideoFile.MAX_SZE,
        ]
        # fmt: on
        for size in valid_sizes:
            mock_stat.return_value.st_size = size
            path = Path()

            # test
            res = validate_video_file(self.unused_ctx, self.unused_param, path)

            # check
            self.assertEqual(res, path)
            mock_stat.assert_called_once()
            mock_stat.reset_mock()


class TestValidateMotionFile(ValidateParamTestCase):

    def test_bad_file_name(self) -> None:

        # setup
        # fmt: off
        bad_paths = [Path(p) for p in [
            "mv", "mv.jpeg", "relative/mv.jpeg", "/absolute/mv.jpeg",
            "Mv", "Mv.jpeg", "relative/Mv.jpeg", "/absolute/Mv.jpeg",
            "mV", "mV.jpeg", "relative/mV.jpeg", "/absolute/mV.jpeg",
            "ba_d", "ba_d.jpeg", "relative/ba_d.jpeg", "/absolute/ba_d.jpeg",
        ]]
        # fmt: on
        for path in bad_paths:

            # check
            with self.assertRaises(BadParameter):

                # test
                validate_motion_file(self.unused_ctx, self.unused_param, path)

    def test_good_file_name(self) -> None:

        # setup
        # fmt: off
        good_paths = [Path(p) for p in [
            "MV", "MV.jpeg", "relative/MV.jpeg", "/absolute/MV.jpeg"
        ]]
        # fmt: on
        for path in good_paths:

            # test
            res = validate_motion_file(self.unused_ctx, self.unused_param, path)

            # check
            self.assertEqual(res, path)


class TestCliFile(TestCase):

    @patch("pathlib.Path.stat")  # brittle test, but easier this way
    @patch("motionphoto.create_motion_photo")
    def test_missing_parameter_option(
        self, mock_stat: MagicMock, mock_create_mp: MagicMock
    ) -> None:
        pass

    @patch("pathlib.Path.stat")  # brittle test, but easier this way
    @patch("motionphoto.create_motion_photo")
    def test_missing_parameter_value(
        self, mock_stat: MagicMock, mock_create_mp: MagicMock
    ) -> None:
        pass

    @patch("motionphoto.create_motion_photo")
    def test_bad_image_format(self, mock_create_mp: MagicMock) -> None:
        pass

    @patch("pathlib.Path.stat")  # brittle test, but easier this way
    @patch("motionphoto.create_motion_photo")
    def test_bad_video_size(
        self, mock_stat: MagicMock, mock_create_mp: MagicMock
    ) -> None:
        pass

    @patch("motionphoto.create_motion_photo")
    def test_bad_motion_name(self, mock_create_mp: MagicMock) -> None:
        pass

    @patch("motionphoto.create_motion_photo")
    def test_bad_timestamp(self, mock_create_mp: MagicMock) -> None:
        pass

    @patch("motionphoto.create_motion_photo")
    def test_good_params(self, mock_create_mp: MagicMock) -> None:
        pass

    @patch("motionphoto.create_motion_photo")
    def test_raise_file_exists_error(self, mock_create_mp: MagicMock) -> None:
        pass

    @patch("motionphoto.create_motion_photo")
    def test_raise_exception(self, mock_create_mp: MagicMock) -> None:
        pass
