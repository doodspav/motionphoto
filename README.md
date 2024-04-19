# motionphoto
Python library for creating Google and Samsung compatible Motion Photos.

Most notably this can be used to convert Live Photos downloaded from iCloud 
(where each photo comes as a separate image and video file) into Motion Photos that users
with Android can use.

## Table of Contents
<!--ts-->
* [Installation](#installation)
* [Usage](#usage)
* [Motion Photo Format](#motion-photo-format)
  * [Google](#google)
  * [Samsung](#samsung)
* [Future](#future)
<!--te-->

## Installation

Linux/MacOS:
```shell
$ python3 -m pip install motionphoto
```

Windows:
```shell
$ py -m pip install motionphoto
```

This library has a dependency on `exiftool`.

Instructions for installing it can be found [here](https://exiftool.org/install.html) and it must be available on
`PATH`, or it can be installed with a package manager.

## Usage

`motionphoto -i <imagePath> -v <videoPath> -m <outputPath> [-t_us <keyFrameOffset> --overwrite]`

Notes:
- `<imagePath>` image format must be JPEG
- `<keyFrameOffset>` is where the image is, in microseconds, from the start of the video file
- `--overwrite` flag allows overwriting an existing file instead of returning an error

## Motion Photo Format
This section will cover the requirements to make a valid Motion Photo.  
Since each application/vendor has their own implementation, they also have separate requirements.

The image format should be JPEG, not HEIC. HEIC occassionally works, but is not reliable.

### Google
Google requires that the video file be embedded inside the image file, however no requirements are
placed on how this should be done. The video file is commonly appended to the end of the image file.

#### Photos
The Google Photos app requires, at a minimum, the following metadata tags to be set on the image:
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

In our case (assuming `tsbsef` is the trailer size before SEF) we want:
```
  head      count      marker                field size      tail
  ∨∨∨∨        ∨  ∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨            ∨∨∨∨∨∨∨       ∨∨∨∨
["SEFH"][106][1][\x00\x00][\x30\x0A][<tsbsef>][<tsbef>][24]["SEFT"]
         ∧∧∧                         ∧∧∧∧∧∧∧∧           ∧∧
       version                     field offset       sef size
```

#### Metadata
The following metadata tags may optionally be set:
- `MotionPhoto`: set to `1`
- `MotionPhotoVersion`: this library sets it to `1`
- `MotionPhotoPresentationTimestampUs`: key-frame time offset in microseconds

Samsung does not place any requirements on the file name.

## Future:
- attempt to parse key frame timestamp from Live Photo (discussed [here]())
- write `XMP-Container:Directory` data for Samsung (discussed [here](https://github.com/exiftool/exiftool/issues/254))
- add support for working with whole directories

