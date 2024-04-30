Basic Usage
===========

Starting out in a directory call ``test`` with an image and a video file
looking like this:

.. code-block:: none

   test
   ├── IMG_1234.JPEG
   └── IMG_1234.MOV

You can combine the image and video files into a single Motion Photo on the
command line by running:

.. code-block:: shell

   motionphoto --image IMG_1234.JPEG --video IMG_1234.MOV --motion MVIMG_1234.JPEG

Alternatively, you can combine the image and video files into a single Motion
Photo in Python by running:

.. code-block:: python

   import motionphoto
   import pathlib

   if __name__ == "__main__":

       motionphoto.create_motion_photo(
           image=pathlib.Path("IMG_1234.JPEG"),
           video=pathlib.Path("IMG_1234.MOV"),
           motion=pathlib.Path("MVIMG_1234.JPEG"),
       )

Running either of these will create a Motion Photo named ``MVIMG_1234.JPEG``
in the test directory, looking like this:

.. code-block:: none

   test
   ├── IMG_1234.JPEG
   ├── IMG_1234.MOV
   └── MVIMG_1234.JPEG

Motion Photos are first and foremost images, so you should keep the extension
from the image file.
