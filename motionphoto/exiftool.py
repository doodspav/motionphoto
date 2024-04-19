import subprocess

from pathlib import Path


def write_metadata_tags(*, media: Path, tags: [str]) -> None:
    """
    Update an existing media file with metadata tags using the command line tool 'exiftool'.

    :param media: Existing input media file whose metadata will be updated with the tags.
    :param tags: List of tags to be written to the media file.

    :raise RuntimeError: Calling 'exiftool' returned a non-zero exit code.
    """

    # short circuit if we don't have any tags
    if not tags:
        return

    # write metadata tags
    config = Path(__file__).resolve().parent / "exiftool.config.pl"
    cmd = ["exiftool", "-config", str(config), "-overwrite_original", "-ignoreMinorErrors", *tags, str(media)]
    res = subprocess.run(cmd, capture_output=True, text=True)

    # handle failure
    if res.returncode != 0:
        msg = f"Command '{' '.join(cmd)}' failed with error: '{res.stderr.rstrip()}'"
        raise RuntimeError(msg)
