# Embedding Containers in images

There are a many reasons for running containerized software in an
in-vehicle context. For example, this allows isolating applications
from each other, and to use different versions of common dependencies
in parallel. To demonstrate how this would look we have some
sample containers and sample images using these.

## Embedding container images

Osbuild (which is used to build the images) allows embedding
containers into the image. Typically these are pulled from an image
registry at build-time, although it is also possible to construct
images as part of the image build.

The org.osbuild.skopeo pipeline stage is used to install the images.
It typically has as input a specific version (digest) of an image
which is pulled from a specified registry. However all the demos
use the mpp-resolve-images feature to resolve a named tag in the
registry instead of hardcoding a particular version, similar to
how mpp-depsolve is used to pick unversioned packages.

A typical container image is stored in the default read-write location
for containers, which is /var/lib/containers/storage. However this is
problematic in some cases. /var is part of the system that is always
writable, and may differ between each user of the image (it has things
like logs in it). This means that /var is not stored as part of an
ostree commit, nor is it generally a good idea for it to be part of a
read-only system partition.

In order to avoid issues with this the sample images use the
`containers-storage` option to store images in
`/usr/share/containers/storage`, modifying the system config options
`additionalimagestores` to point to that. This allows storing and
using the built-in containers as read-only containers in an ostree
system while also allowing other containers to be installed at
runtime.

## Running containers

Once a container is embedded in a system image it can be started
manually with `podman run imagename`. However, it doesn't
automatically start at boot. In order to be started automatically we
have to create a systemd service that starts the container, at the
right time, in the right way.

The sample images use [quadlet](https://github.com/containers/quadlet)
to set up the systemd services. This is a tool that takes an easy to
understand and maintain container unit description and automatically
generates (at boot time) and uses the corresponding systemd service
unit file. Using this makes it very easy to automatically start a
container at system boot, you just put a file in `/etc/containers/systemd`

## The containers

The `containers` directory has some example containers that are used
in the sample images. They are currently manually built, and then
stored in the [automotive-sig
registry](https://gitlab.com/redhat/automotive/automotive-sig/container_registry)
for use by the sample manifests.

Currently the container demoed are:

*  `containers/nginx-demo`:
  Sample nginx demos that servers a "hello world" html file. Based on CS9.


## The images

* `container.mpp.yml`

This image demonstrate how the nginx-demo container is embedded into
the image at a custom location, how to configure podman to pick that
location up, and how to start the container at boot.
