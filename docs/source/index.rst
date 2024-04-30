.. motionphoto documentation master file, created by
   sphinx-quickstart on Sat Apr 27 04:30:59 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to motionphoto's documentation!
=======================================

This package contains a Python library and helper executables to convert image-video pairs into Motion Photos
viewable in Google Photos, Google Gallery, and Samsung Gallery, as well as other Android photo viewers.

The key motivation for using this library is to convert iOS Live Photos into Android Motion Photos.

.. warning::
   If you are downloading Live Photos from iCloud to convert to Motion Photos, you must download them as
   **Most Compatible** which will download the images as JPEG instead of HEIC.

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   getting_started/installation
   getting_started/basic_usage

.. toctree::
   :maxdepth: 1
   :caption: Executable Interface

   executable_interface/motionphoto
   executable_interface/motionphotodir

.. toctree::
   :maxdepth: 1
   :caption: Python API

   python_api/top_level
   python_api/motion
   python_api/google
   python_api/samsung

.. toctree::
   :maxdepth: 1
   :caption: Binary Specification

   binary_specification/general
   binary_specification/google
   binary_specification/samsung

.. toctree::
   :maxdepth: 1
   :caption: Notes

   notes/changelog
