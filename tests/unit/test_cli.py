import os

from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click import Context, Option, BadParameter
from click.testing import CliRunner

import motionphoto

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

    MAX_SIZE: int = 2**31 - 1

    @patch("pathlib.Path.stat")
    def test_size_too_large(self, mock_stat: MagicMock) -> None:

        # setup
        mock_stat.return_value.st_size = TestValidateVideoFile.MAX_SIZE + 1
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
            -2 * TestValidateVideoFile.MAX_SIZE, TestValidateVideoFile.MAX_SIZE,
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

    def setUp(self) -> None:

        # create required files
        with NamedTemporaryFile("r", suffix=".jpeg", delete=False) as f:
            self.image_path = Path(f.name)
            self._image_path_to_delete = deepcopy(self.image_path)
        with NamedTemporaryFile("r", suffix=".mov", delete=False) as f:
            self.video_path = Path(f.name)
            self._video_path_to_delete = deepcopy(self.video_path)
        self.motion_path = Path("MV.jpeg")

        # set permissions (read-only input files)
        self.image_path.chmod(0o400)
        self.video_path.chmod(0o400)

        # check everything
        for p in [self.image_path, self.video_path]:
            self.assertTrue(p.exists())
            self.assertTrue(os.access(p, os.R_OK))
            self.assertFalse(os.access(p, os.W_OK))
            self.assertFalse(os.access(p, os.X_OK))
        self.assertLessEqual(
            self.video_path.stat().st_size, TestValidateVideoFile.MAX_SIZE
        )
        self.assertFalse(self.motion_path.exists())

    def tearDown(self) -> None:

        # remove files we created
        os.remove(self._image_path_to_delete)
        os.remove(self._video_path_to_delete)
        for p in [self.image_path, self.video_path, self.motion_path]:
            if p.exists():
                os.remove(p)

    @patch("motionphoto.cli.create_motion_photo")
    def test_missing_parameter_option(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        param_pairs = [
            ("-i", str(self.image_path)),
            ("-v", str(self.video_path)),
            ("-m", str(self.motion_path)),
        ]
        for i in range(len(param_pairs)):
            use_param_pairs = deepcopy(param_pairs)
            use_param_pairs.pop(i)
            use_params = [p for pp in use_param_pairs for p in pp]

            # test
            res = runner.invoke(cli_file, use_params)

            # check
            self.assertNotEqual(res.exit_code, 0)
            for pp in param_pairs:
                if pp[0] == param_pairs[i][0]:
                    self.assertIn(pp[0], res.output)
                else:
                    self.assertNotIn(pp[0], res.output)
            mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_missing_parameter_value(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        param_pairs = [
            ("-i", str(self.image_path)),
            ("-v", str(self.video_path)),
            ("-m", str(self.motion_path)),
        ]
        for i in range(len(param_pairs)):
            use_param_pairs = deepcopy(param_pairs)
            use_param_pairs[i] = (use_param_pairs[0],)
            use_params = [p for pp in use_param_pairs for p in pp]

            # test
            res = runner.invoke(cli_file, use_params)

            # check
            self.assertNotEqual(res.exit_code, 0)
            for pp in param_pairs:
                if pp[0] == param_pairs[i][0]:
                    self.assertIn(pp[0], res.output)
                else:
                    self.assertNotIn(pp[0], res.output)
            mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_bad_image_format(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        with NamedTemporaryFile("r", suffix=".not_jpeg") as f:
            self.image_path = Path(f.name)
            params = [
                # fmt: off
                "-i", str(self.image_path),
                "-v", str(self.video_path),
                "-m", str(self.motion_path),
                # fmt: on
            ]

            # test
            res = runner.invoke(cli_file, params)

            # check
            self.assertNotEqual(res.exit_code, 0)
            self.assertIn("-i", res.output)
            for p in ["-v", "-m"]:
                self.assertNotIn(p, res.output)
            mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_unreadable_image(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        self.image_path.chmod(0o200)
        self.assertFalse(os.access(self.image_path, os.R_OK))
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("-i", res.output)
        for p in ["-v", "-m"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_non_existent_image(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        self.image_path = Path("non_existent.jpeg")
        self.assertFalse(self.image_path.exists())
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("-i", res.output)
        for p in ["-v", "-m"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    @patch("pathlib.Path.stat")  # brittle test, but easier than making 2GB file
    def test_bad_video_size(
        self, mock_stat: MagicMock, mock_create_mp: MagicMock
    ) -> None:

        # setup
        runner = CliRunner()
        mock_stat.return_value.st_size = TestValidateVideoFile.MAX_SIZE + 1
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            # fmt: on
        ]
        self.assertGreater(
            self.video_path.stat().st_size, TestValidateVideoFile.MAX_SIZE
        )
        mock_stat.reset_mock()

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("-v", res.output)
        for p in ["-i", "-m"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()
        mock_stat.assert_called_once()

    @patch("motionphoto.cli.create_motion_photo")
    def test_unreadable_video(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        self.video_path.chmod(0o200)
        self.assertFalse(os.access(self.video_path, os.R_OK))
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("-v", res.output)
        for p in ["-i", "-m"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_non_existent_video(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        self.video_path = Path("non_existent.mov")
        self.assertFalse(self.video_path.exists())
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("-v", res.output)
        for p in ["-i", "-m"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_bad_motion_name(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        self.motion_path = Path("not_MV.jpeg")
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            # fmt: on
        ]
        self.assertFalse(self.motion_path.exists())

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("-m", res.output)
        for p in ["-i", "-v"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_readonly_writeonly_motion(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        with NamedTemporaryFile("r", prefix="MV") as f:
            perms = [
                (0o200, os.R_OK),  # write-only, read check
                (0o400, os.W_OK),  # read-only, write check
            ]
            for perm in perms:
                self.motion_path = Path(f.name)
                self.motion_path.chmod(perm[0])
                self.assertFalse(os.access(self.motion_path, perm[1]))
                params = [
                    # fmt: off
                    "-i", str(self.image_path),
                    "-v", str(self.video_path),
                    "-m", str(self.motion_path),
                    "--overwrite",
                    # fmt: on
                ]

                # test
                res = runner.invoke(cli_file, params)

                # check
                self.assertNotEqual(res.exit_code, 0)
                self.assertIn("-m", res.output)
                for p in ["-i", "-v"]:
                    self.assertNotIn(p, res.output)
                mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_bad_timestamp(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        timestamp_us = -1
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            "-t_us", timestamp_us,
            # fmt: on
        ]
        self.assertLess(timestamp_us, 0)

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("-t_us", res.output)
        for p in ["-i", "-v", "-m"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_both_bool_option_overwrite_last(
        self, mock_create_mp: MagicMock
    ) -> None:

        # setup
        runner = CliRunner()
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            "--no-overwrite",
            "--overwrite",
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertEqual(res.exit_code, 0)
        mock_create_mp.assert_called_once_with(
            image=self.image_path,
            video=self.video_path,
            motion=self.motion_path,
            timestamp_us=None,
            overwrite=True,
        )

    @patch("motionphoto.cli.create_motion_photo")
    def test_both_bool_option_no_overwrite_last(
        self, mock_create_mp: MagicMock
    ) -> None:

        # setup
        runner = CliRunner()
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            "--overwrite",
            "--no-overwrite",
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertEqual(res.exit_code, 0)
        mock_create_mp.assert_called_once_with(
            image=self.image_path,
            video=self.video_path,
            motion=self.motion_path,
            timestamp_us=None,
            overwrite=False,
        )

    @patch("motionphoto.cli.create_motion_photo")
    def test_duplicate_option(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        params = [
            # fmt: off
            "-i", "bad.txt",
            "-i", str(self.image_path),
            "-v", "bad.mov",
            "-v", str(self.video_path),
            "-m", "bad.jpeg",
            "-m", str(self.motion_path),
            "-t_us", -1,
            "-t_us", 1234,
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertEqual(res.exit_code, 0)
        mock_create_mp.assert_called_once_with(
            image=self.image_path,
            video=self.video_path,
            motion=self.motion_path,
            timestamp_us=1234,
            overwrite=False,
        )

    @patch("motionphoto.cli.create_motion_photo")
    def test_unknown_option(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            "--unknown_option",
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn(params[-1], res.output)
        for p in ["-i", "-v", "-m"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_unknown_argument(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            "unknown_argument",
            # fmt: on
        ]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn(params[-1], res.output)
        for p in ["-i", "-v", "-m"]:
            self.assertNotIn(p, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_good_params(self, mock_create_mp: MagicMock) -> None:
        pass

    @patch("motionphoto.cli.create_motion_photo")
    def test_raise_file_exists_error(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        params = [
            # fmt: off
            "-i", str(self.image_path),
            "-v", str(self.video_path),
            "-m", str(self.motion_path),
            # fmt: on
        ]
        mock_create_mp.side_effect = lambda *args, **kwargs: (
            _ for _ in ()
        ).throw(FileExistsError())

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("--overwrite", res.output)  # should contain tip
        mock_create_mp.assert_called_once_with(
            image=self.image_path,
            video=self.video_path,
            motion=self.motion_path,
            timestamp_us=None,
            overwrite=False,
        )

    @patch("motionphoto.cli.create_motion_photo")
    def test_raise_exception(self, mock_create_mp: MagicMock) -> None:
        pass

    @patch("motionphoto.cli.create_motion_photo")
    def test_version(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        params = ["--version"]

        # test
        res = runner.invoke(cli_file, params)

        # check
        self.assertEqual(res.exit_code, 0)
        self.assertIn(motionphoto.__version__, res.output)
        mock_create_mp.assert_not_called()

    @patch("motionphoto.cli.create_motion_photo")
    def test_help(self, mock_create_mp: MagicMock) -> None:

        # setup
        runner = CliRunner()
        params = ["--help"]

        # test
        res = runner.invoke(cli_file, params)

        # check
        options = [
            "-i, --image",
            "-v, --video",
            "-m, --motion",
            "-t_us, --timestamp_us",
            "--overwrite / --no-overwrite",
            "--version",
            "--help",
        ]
        for option in options:
            self.assertIn(option, res.output)
        mock_create_mp.assert_not_called()
