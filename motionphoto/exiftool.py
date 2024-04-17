import subprocess

from pathlib import Path


def write_metadata_tags(media: Path, tags: [str]) -> None:

    # write metadata tags
    config = Path(__file__).resolve().parent / "exiftool.config.pl"
    cmd = ["exiftool", "-config", str(config), "-overwrite_original", "-ignoreMinorErrors", *tags, str(media)]
    res = subprocess.run(cmd, capture_output=True, text=True)

    # handle failure
    if res.returncode != 0:
        msg = f"Command '{' '.join(cmd)}' failed with error: {res.stderr}"
        raise RuntimeError(msg)
