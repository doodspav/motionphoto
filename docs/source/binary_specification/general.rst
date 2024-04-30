General
=======

| This section will cover the reverse engineered binary specification of Motion
  Photos.
| This section is solely for information, and is **NOT required to use the
  package**.

| Since each application/vendor has their own implementation, they also have
  separate specifications.
| Luckily, all current implementations are compatible with each other, so
  Motion Photos created by this library will work transparently across
  applications from different vendors without any input needed from the user.

| The two main vendors of Motion Photos are Google and Samsung.
| Their implementation of the Motion Photo format will be detailed in the
  following sections.

.. note::
   Theoretically HEIC images can be used to create Motion Photos. Unfortunately
   this does not work consistently, so this library currently requires that the
   image files be JPEG.
