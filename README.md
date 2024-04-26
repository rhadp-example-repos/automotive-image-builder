# Automotive image builder

Automotive image builder is a tool to create various kinds of OS
images based on CentOS derived OSes. The images can support
package-based mode (called "regular") as well as image-based mode
(called "ostree").

The main tool is called `automotive-image-builder`, and the basic
operation it does is called "composing" manifests. The compose
operation takes a yaml-based automotive image manifest, as well as a
set of options affecting the compose and resolves the manifest into an
osbuild json file. This json file is a precise build instruction for
how to build an image with osbuild with the very specific software
that was chosen during the compose. For example, the version of
selected packages and container images is chosen during the compose.

For example, to build a qcow2 image you can run:

 $ automotive-image-builder compose --distro cs9 --image-type regular --target qemu my-image.mpp.yml osbuild.json
 $ sudo osbuild --store osbuild_store --output-directory output --export qcow2 osbuild.json

This will first compose the osbuild.json file, and then build it and export the "qcow2" output, which
will end up in the "output" directory (in particular as output/qcow2/disk.qcow2). You an then run it
using:

 $ automotive-image-runner  output/qcow2/disk.qcow2

The sample-images repository (https://gitlab.com/CentOS/automotive/sample-images) has a lot of
example images, as well as a Makefile that makes it easy to build those images.
