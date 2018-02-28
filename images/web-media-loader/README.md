# The media-loader image
Copies media files to a mounted volume. Place your media files into
the `media` directory (feel free to use `.tar.gz` to save space
as the build will automatically unpack them) but consider adding the
files to the project's `.gitignore`.

>   This is can be a massive image at around 12.2GB (at the time of writing)

It expects a volume mount at `/media-volume`.

## Building
Build with...

    $ docker build . -t xchem/fragalysis-stack-media-loader:1.0.0
