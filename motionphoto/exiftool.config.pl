%Image::ExifTool::UserDefined = (

    # XMP tags for Motion Photo
    'Image::ExifTool::XMP::GCamera' => {

        # Google
        MicroVideo                        => { Writable => 'integer' },
        MicroVideoVersion                 => { Writable => 'integer' },
        MicroVideoOffset                  => { Writable => 'integer' },
        MicroVideoPresentationTimestampUs => { Writable => 'integer' },

        # Samsung
        MotionPhoto                        => { Writable => 'integer' },
        MotionPhotoVersion                 => { Writable => 'integer' },
        MotionPhotoPresentationTimestampUs => { Writable => 'integer' },
    },
);

1;  # end
