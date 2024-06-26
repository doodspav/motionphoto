# motionphoto
Python library for creating Google and Samsung compatible Motion Photos.

Most notably this can be used to convert Live Photos downloaded from iCloud 
(where each photo comes as a separate image and video file) into Motion Photos that users
with Android can experience.

## Table of Contents
<!--ts-->
* [Dependencies](#dependencies)
* [Installation](#installation)
* [Usage](#usage)
* [Technical Implementation Details](#technical-implementation-details)
  * [Google](#google)
  * [Samsung](#samsung)
* [Future](#future)
<!--te-->

## Dependencies

This library has a dependency on the `exiftool` executable by Phil Harvey.

Instructions for installing `exiftool` can be found [here](https://exiftool.org/install.html), and it must be installed
on `PATH`. Alternatively, it can be installed using a package manager.

## Installation

Linux/MacOS:
```shell
$ python3 -m pip install motionphoto
```

Windows:
```shell
$ py -m pip install motionphoto
```

If you run either command with the system installation of Python rather than in a virtual environment, you may need to
append `--break-system-packages` to the end of the command.

## Usage

### Executable

The `motionphoto` executable takes the following options:
- `-i/--image <imagePath>`: **(required)** an existing readable JPEG file which will become the key-frame
- `-v/--video <videoPath>`: **(required)** an existing readable file, no bigger than `INT32_MAX` bytes
- `-m/--motion <outputPath>`: **(required)** a readable and writable path, file must not exist unless `--overwrite`
- `-t_us/--timestamp_us <keyFrameOffset>`: _(optional)_ key-frame time offset in microseconds from the start of the video
- `--(no-)overwrite/`: _(optional)_ permit `<outputPath>` to be an existing file and overwrite it instead of returning an error

Note: `<outputPath>`'s file name must start with `MV`.

Putting that together we get this:
```shell
$ motionphoto -i <imagePath> -v <videoPath> -m <outputPath> [-t_us <keyFrameOffset> --(no-)overwrite]
```

Which with dummy parameters, a minimal example might look like this:
```shell
$ motionphoto -i "data/IMG_1234.JPEG" -v "data/IMG_1234.MOV" -m "data/MVIMG_1234.JPEG"
```

For the version run `motionphoto --version`, and for more information run `motionphoto --help`.

### Python

There is a single core function available as:
```python
from motionphoto import create_motion_photo
```

Documentation for how to use it can be found in the function's docstring, but the API is fairly
self-explanatory:
```python
from pathlib import Path
from typing import Optional

def create_motion_photo(*, image: Path, video: Path, motion: Path,
                        timestamp_us: Optional[int] = None, overwrite: bool = False) -> None:
    pass
```

## Technical Implementation Details
This section will cover the reverse engineered binary specification of Motion Photos.  
This section is solely for information, and is NOT required to use the library.

Since each application/vendor has their own implementation, they also have separate specifications.
The Motion Photos created by this library will work transparently across vendors without any input
needed from the user. 

The only common requirement is that the image format should be JPEG, not HEIC. HEIC occasionally
works but is not reliable. This is already enforced by the library.

### Google
Google requires that the video file be embedded inside the image file, however no requirements are
placed on how this should be done. The video file is commonly appended to the end of the image file.

#### Photos
The Google Photos app, at a minimum, requires the following metadata tags to be set on the image:
- `MicroVideo`: set to `1`
- `MicroVideoVersion`: this library sets it to `1`
- `MicroVideoOffset`: offset in bytes from the end of the Motion Photo file to the start of the embedded video file

The offset is encoded as an XML field, so it does not impose any limit on the video size.

The additional metadata tag may be optionally set if known, may be set to `-1` if unknown, or may
be omitted entirely:
- `MicroVideoPresentationTimestampUs`: key-frame time offset in microseconds

#### Gallery
The Google Gallery app additionally requires that the Motion Photo filename start with `MV`.

### Samsung
Samsung requires that the video file be embedded inside the image file by constructing a trailer in a custom
format and appending it to the end of the image file.  
It **MUST** be the last trailer in the image file.

#### Trailer Data
Trailer fields are written sequentially in the following format:
```
[\x00\x00][marker_value(ule16)][name_size(ule32)][name][data]
```
In our case we want:
```
                  name size              raw video file
                     ∨∨                      ∨∨∨∨∨
[\x00\x00][\x30\x0A][16]["MotionPhoto_Data"][<bin>]
 ∧∧∧∧∧∧∧∧∧∧∧∧∧∧∧∧∧∧      ∧∧∧∧∧∧∧∧∧∧∧∧∧∧∧∧∧∧
       marker                   name
```
Additional fields can be found [here](https://github.com/exiftool/exiftool/blob/ecc573fc04ac6538802fd0a61a9c4ca53837ca1d/lib/Image/ExifTool/Samsung.pm#L945)
but are not necessary.

#### Trailer Check
The trailer also has an additional SEF section that contains the sizes of fields and is used for validation.
It is appended directly after the fields, and has the following format:  
```
["SEFH"][version(ule32)][field_count(ule32)]
for each field: [\x00\x00][field_marker_value(ule16)][field_offset_from_sef(ule32)][field_size(ule32)]
[sef_size(ule32)]["SEFT"]
```
The `sef_size` is the size of that whole section not including `"SEFH"` and `"SEFT"` (head and tail markers).

In our case (assuming `tsbsef` is the trailer size before the start of the SEF section), we want:
```
  head      count      marker                field size      tail
  ∨∨∨∨        ∨  ∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨            ∨∨∨∨∨∨∨       ∨∨∨∨
["SEFH"][106][1][\x00\x00][\x30\x0A][<tsbsef>][<tsbef>][24]["SEFT"]
         ∧∧∧                         ∧∧∧∧∧∧∧∧           ∧∧
       version                     field offset       sef size
```

The `field_size` and `field_offset` are both encoded as little-endian 32bit integers. This imposes a limit on the size
of the video file, namely that its size (plus the start of the SEF section) cannot exceed `2 ^ 32 - 1`.

#### Metadata
The following metadata tags may optionally be set:
- `MotionPhoto`: set to `1`
- `MotionPhotoVersion`: this library sets it to `1`
- `MotionPhotoPresentationTimestampUs`: key-frame time offset in microseconds

Samsung does not place any requirements on the file name.
