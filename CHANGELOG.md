# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [NEXT] [Major] - 2024-04-10
### Info
- Initial release
- Implementation is Python script calling `exiftool`
- Requires `exiftool` to be installed on `PATH` by the user
### Added
- Initial python interface (`motionphoto` package):
  - `.`: 
    - `create_motion_photo(...)`
  - `.samsung`: 
    - `SamsungMarker`
    - `SamsungTag`
    - `SamsungTrailer`
    - `create_samsung_motion_trailer(...)`
    - `write_samsung_motion_metadata(...)`
  - `.google`:
    - `write_google_motion_metadata(...)`
  - `.exiftool`:
    - `write_metadata_tags(...)`
- Initial executable interface (`motionphoto` executable):
  - `-i/--image <imagePath>`: (required) must be an existing readable JPEG image file
  - `-v/--video <videoPath>`: (required) must be an existing readable file, no bigger than INT32_MAX bytes
  - `-m/--motion <outputPath>`: (required) must be a readable and writable path, must not exist unless `--overwrite`
  - `-t_us/--timestamp_us <keyFrameOffset>`: (optional) key-frame time offset in microseconds
  - `--(no-)overwrite`: (optional) permit `outputPath` to be an existing file and overwrite it instead of returning an error
