Google
======

| Google requires that the video file be embedded inside the image file,
  however no requirements are placed on how this should be done.
| The video file is commonly appended to the end of the image file.

Google Photos
-------------

The Google Photos app, at a minimum, requires the following metadata tags to be
set on the image:

- ``MicroVideo``: set to ``1``
- ``MicroVideoVersion``: this library sets it to ``1``
- ``MicroVideoOffset``: offset in bytes from the end of the Motion Photo file
  to the start of the embedded video file

The ``MicroVideoOffset`` is encoded as an XML field, so it does not impose any
limit on the video size in bytes.

The additional metadata tag may be optionally set if known, may be set to
``-1`` if unknown, or may be omitted entirely:

- ``MicroVideoPresentationTimestampUs``: key-frame time offset in microseconds

Google Gallery
--------------

The Google Gallery app additionally requires that the Motion Photo filename
starts with ``MV``.
