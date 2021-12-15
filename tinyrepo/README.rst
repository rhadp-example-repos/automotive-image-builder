Tinyrepo
========

This folder contains some utility scripts that are used to sample images that
can be easily downloaded and used.

## Creating sample images

The sample images are a sub-set of the images one can build using the osbuild
manifest present in this repository.

The creating of the images is handled by the `build_images.sh` shell script
which simply calls sequentially different `make` commands, then compress the
resulting images and places them in a timestamped directory available to apache.
Finally, it creates a symlink between the newest folder and a `latest` folder,
thus giving a stable location where one can find the most recently built images.


## Cron job

The `build_images.sh` shell script present in this folder are ran via the
following cron job configuration:

::

  0 2 * * 1 sh /path/to/automotive-sig/tinyrepo/build_images.sh /path/to/clone/of/automotive-sig/osbuild-manifests/ /path/to/root/folder/in/apache


This allows to build new images weekly.


