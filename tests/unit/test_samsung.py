import struct

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch

from motionphoto.samsung import (
    SamsungTrailer,
    create_samsung_motion_trailer,
    write_samsung_motion_metadata,
)


class TestWriteSamsungMotionMetadata(TestCase):

    def make_tags(self, *, timestamp_us: Optional[int]) -> List[str]:
        tags = [
            "-MotionPhoto=1",
            "-MotionPhotoVersion=1",
        ]
        if timestamp_us is not None:
            tags.append(f"-MotionPhotoPresentationTimestampUs={timestamp_us}")
        return tags

    @patch("motionphoto.samsung.write_metadata_tags")
    def test_timestamp_int(self, mock_tags: MagicMock) -> None:

        # setup
        media = Path("media")
        timestamp_values = [-(2**3), -10, 0, 10, 2**33]
        for timestamp in timestamp_values:
            tags = self.make_tags(timestamp_us=timestamp)

            # test
            write_samsung_motion_metadata(media=media, timestamp_us=timestamp)

            # check
            mock_tags.assert_called_once_with(media=media, tags=tags)
            mock_tags.reset_mock()

    @patch("motionphoto.samsung.write_metadata_tags")
    def test_timestamp_none(self, mock_tags: MagicMock) -> None:

        # setup
        media = Path("media")
        timestamp = None
        tags = self.make_tags(timestamp_us=timestamp)

        # test
        write_samsung_motion_metadata(media=media, timestamp_us=timestamp)

        # check
        mock_tags.assert_called_once_with(media=media, tags=tags)
        mock_tags.reset_mock()


class TestCreateSamsungMotionTrailer(TestCase):

    MAX_SIZE = 2**31 - 1  #

    def make_trailer(self, *, media_contents: bytes) -> SamsungTrailer:
        trailer = bytearray()
        # main part
        trailer += (
            b"\x00\x00\x30\x0A"  # marker
            + struct.pack("<I", 16)  # size
            + b"MotionPhoto_Data"  # data
            + media_contents  # file
        )
        main_part_size = len(trailer)
        # sef part
        trailer += (
            b"SEFH"  # marker (head)
            + struct.pack("<I", 106)  # version
            + struct.pack("<I", 1)  # field count
            + b"\x00\x00\x30\x0A"  # marker
            + struct.pack("<I", main_part_size)  # negative offset
            + struct.pack("<I", main_part_size)  # field size
            + struct.pack("<I", 24)  # sef size
            + b"SEFT"  # marker (tail)
        )
        return SamsungTrailer(
            data=bytes(trailer), negative_video_offset=len(trailer) - 24
        )

    @patch("pathlib.Path.stat")
    def test_media_size_too_large(self, mock_stat: MagicMock) -> None:

        # setup
        media = Path("media")
        mock_stat.return_value.st_size = (
            TestCreateSamsungMotionTrailer.MAX_SIZE + 1
        )
        self.assertGreater(
            media.stat().st_size, TestCreateSamsungMotionTrailer.MAX_SIZE
        )
        mock_stat.reset_mock()

        # check
        with self.assertRaises(ValueError):

            # test
            create_samsung_motion_trailer(video=media)

        # check
        mock_stat.assert_called()

    @patch("pathlib.Path.stat")
    def test_media_size_limit(self, mock_stat: MagicMock) -> None:

        # setup
        with NamedTemporaryFile("rb+") as f:
            data = b"abc"
            f.write(data)
            f.flush()
            media = Path(f.name)
            mock_stat.return_value.st_size = (
                TestCreateSamsungMotionTrailer.MAX_SIZE
            )
            self.assertLessEqual(
                media.stat().st_size, TestCreateSamsungMotionTrailer.MAX_SIZE
            )
            mock_stat.reset_mock()

            # test
            trailer = create_samsung_motion_trailer(video=media)

            # check
            mock_stat.assert_called_once()
            expected_trailer = self.make_trailer(media_contents=data)
            self.assertEqual(expected_trailer, trailer)
            offset = len(trailer.data) - trailer.negative_video_offset
            self.assertEqual(data, trailer.data[offset : offset + len(data)])

    def test_good_media(self) -> None:

        # setup
        data_values = [
            b"",
            b"wjnfweoijfwpoijedpowiejfowijefoi",
            b"\x00",
            b"\x00wowffo\x00woenfwioe\x11jeronferfo\x01ewrfn\x00",
        ]
        for data in data_values:
            with NamedTemporaryFile("rb+") as f:
                f.write(data)
                f.flush()
                media = Path(f.name)
                self.assertLessEqual(
                    media.stat().st_size,
                    TestCreateSamsungMotionTrailer.MAX_SIZE,
                )

                # test
                trailer = create_samsung_motion_trailer(video=media)

                # check
                expected_trailer = self.make_trailer(media_contents=data)
                self.assertEqual(expected_trailer, trailer)
                offset = len(trailer.data) - trailer.negative_video_offset
                self.assertEqual(
                    data, trailer.data[offset : offset + len(data)]
                )
