from pathlib import Path
from typing import List
from unittest import TestCase
from unittest.mock import MagicMock, patch

from motionphoto.google import write_google_motion_metadata


class TestWriteGoogleMotionMetadata(TestCase):

    def make_tags(self, *, offset: int, timestamp_us: int) -> List[str]:
        return [
            "-MicroVideo=1",
            "-MicroVideoVersion=1",
            f"-MicroVideoOffset={offset}",
            f"-MicroVideoPresentationTimestampUs={timestamp_us}",
        ]

    @patch("motionphoto.google.write_metadata_tags")
    def test_offset(self, mock_tags: MagicMock) -> None:

        # setup
        media = Path("media")
        offset_values = [-(2**33), -10, 0, 10, 2**33]
        timestamp = 0
        for offset in offset_values:
            tags = self.make_tags(offset=offset, timestamp_us=timestamp)

            # test
            write_google_motion_metadata(
                media=media,
                negative_video_offset=offset,
                timestamp_us=timestamp,
            )

            # check
            mock_tags.assert_called_once_with(media=media, tags=tags)
            mock_tags.reset_mock()

    @patch("motionphoto.google.write_metadata_tags")
    def test_timestamp_int(self, mock_tags: MagicMock) -> None:

        # setup
        media = Path("media")
        offset = 0
        timestamp_values = [-(2**33), -10, 0, 10, 2**33]
        for timestamp in timestamp_values:
            tags = self.make_tags(offset=offset, timestamp_us=timestamp)

            # test
            write_google_motion_metadata(
                media=media,
                negative_video_offset=offset,
                timestamp_us=timestamp,
            )

            # check
            mock_tags.assert_called_once_with(media=media, tags=tags)
            mock_tags.reset_mock()

    @patch("motionphoto.google.write_metadata_tags")
    def test_timestamp_none(self, mock_tags: MagicMock) -> None:

        # setup
        media = Path("media")
        offset = 0
        tags = self.make_tags(offset=offset, timestamp_us=-1)

        # test
        write_google_motion_metadata(
            media=media, negative_video_offset=offset, timestamp_us=None
        )

        # check
        mock_tags.assert_called_once_with(media=media, tags=tags)
        mock_tags.reset_mock()
