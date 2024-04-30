Samsung
=======

| Samsung requires that the video file be embedded inside the image file by
  constructing a trailer in a custom format, and appending it to the end of the
  image file.

.. warning::
   The Samsung Motion Photo trailer **MUST** be the last trailer in the image
   file.

Trailer Data
------------

Trailer fields are written sequentially in the following binary format:

.. code-block:: c

   struct field_t {
       uint16_t _zeros = 0;
       uint16_t marker_value;  // little-endian
       uint32_t name_size;     // little-endian
       uint8_t name[name_size];
       uint8_t data[];
   };

In our case, we want:

.. code-block:: c

   struct field_t field {
       ._zeros = 0,
       .marker_value = 0x0a30,
       .name_size = 16,
       .name = "MotionPhoto_Data",  // no null-terminator
       .data = "<raw video file>"
   };

Additional fields can be found
`here <https://github.com/exiftool/exiftool/blob/ecc573fc04ac6538802fd0a61a9c4ca53837ca1d/lib/Image/ExifTool/Samsung.pm#L945>`_
but are not necessary.

Trailer Check
-------------

| The trailer additionally has an SEF section that contains the sizes of the
  complete fields, and is used for performing validation checks.
| It is appended directly after the fields, and has the following format:

.. code-block:: c

   struct sef_field_t {
       uint16_t _zeros = 0;
       uint16_t marker_value;           // little-endian
       uint32_t field_offset_from_sef;  // little-endian
       uint32_t field_size;             // little-endian
   };

   struct sef_t {
       uint8_t _head[4] = "SEFH";               // no null-terminator
       uint32_t version;                        // little-endian
       uint32_t field_count;                    // little-endian
       struct sef_field_t fields[field_count];
       uint32_t size;                           // little-endian
       uint8_t _tail[4] = "SEFT";               // no null-terminator
   };

The ``size`` field in ``sef_t`` is the size of that whole serialized ``sef_t``
struct not including the ``_head`` and ``_tail`` members.

In our case, assuming that the trailer data only has a single field based on
the example in the previous section, and that the complete size of this field
when serialized is ``N`` bytes, we want:

.. code-block:: c

   struct sef_field_t sef_field {
       ._zeros = 0,
       .marker_value = 0x0a30,
       .field_offset_from_sef = N,
       .field_size = N
   };

   struct sef_t sef {
       ._head = "SEFH",          // no null-terminator
       .version = 106,
       .field_count = 1,
       .fields = { sef_field },
       .size = sizeof(sef) - 8,
       ._tail = "SEFT"           // no null-terminator
   };

.. note::
   The ``field_size`` and ``field_offset_from_sef`` members are both encoded as
   32bit integers. This imposes a limit on the size of the video file (which
   is enforced by this library).

Metadata
--------

The following metadata tags may optionally be set:

- ``MotionPhoto``: set to ``1``
- ``MotionPhotoVersion``: this library sets it to ``1``
- ``MotionPhotoPresentationTimestampUs``: key-frame time offset in microseconds

Other
-----

Samsung does not place any requirements on the file name.
