from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase
from unittest.mock import MagicMock, patch

from motionphoto.exiftool import write_metadata_tags


class TestWriteMetadataTags(TestCase):

    @patch("subprocess.run")
    def test_non_zero_exit(self, mock_run: MagicMock) -> None:

        # setup
        media = Path("media")
        tags = ["test"]
        exit_codes = [-2, -1, 1, 2]
        for ec in exit_codes:
            mock_run.return_value = CompletedProcess(
                args=[], returncode=ec, stdout="stdout", stderr="stderr"
            )

            # check
            with self.assertRaisesRegex(RuntimeError, ".*stderr.*"):

                # test
                write_metadata_tags(media=media, tags=tags)

            # check
            mock_run.assert_called_once()
            mock_run.reset_mock()

    @patch("subprocess.run")
    def test_no_tags_skipped(self, mock_run: MagicMock) -> None:

        # setup
        media = Path("media")
        tags = []
        exit_code = -1  # would normally raise an exception
        mock_run.return_value = CompletedProcess(args=[], returncode=exit_code)

        # test
        write_metadata_tags(media=media, tags=tags)

        # check
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_tags_good_exit(self, mock_run: MagicMock) -> None:

        # setup
        media = Path("media")
        tags = ["test"]
        exit_code = 0
        mock_run.return_value = CompletedProcess(args=[], returncode=exit_code)

        # test
        write_metadata_tags(media=media, tags=tags)

        # check
        mock_run.assert_called_once()
