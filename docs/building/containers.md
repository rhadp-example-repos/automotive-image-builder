# Containers in automotive

## Background

The automotive industry is moving towards a new architectural concept
called "Software Defined Vehicles" (SDV). Part of this is a software model
that is similar to the micro-server architecture used in the cloud. In
this model, the various services and application running in the car
are separate, isolated entities that expose a well defined
interfaces. The whole system is then made of a large collection of
such services which interact using some form of networking protocol,
most commonly [SOME/IP](https://some-ip.com/), which is a message
based protocol with a [pub/sub
model](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
running on top of IP and/or unix domain sockets.

While the SDV model can be implemented with traditional methods, it
(similarly to micro-services) lends itself extremely well to the use of
containers, because the isolation aspects of containers matches well
to the separated services and the requirement of well-defined declared
interfaces between containers.

In addition, containers have other advantages, such as the ability for
each container to use different versions of dependencies and the
improved robustness, security and flexibility that comes from the
kernel-level application isolation.

## Sample container image

To demonstrate how to implement this we have the
[container.mpp.yml](https://gitlab.com/redhat/automotive/automotive-sig/-/blob/main/osbuild-manifests/cs9/container.mpp.yml)
image and some [sample
applications](https://gitlab.com/redhat/automotive/automotive-sig/-/tree/main/sample-apps).

The sample-apps consists of two SOME/IP services: `radio-service`,
which simulates a radio and `engine-service` that simulates other
parts of the car. There is also a command line application
`radio-client` which talks to the services displaying the current
status and allowing you to control the radio. For more details about
these apps, see the
[README](https://gitlab.com/redhat/automotive/automotive-sig/-/blob/someip-samples/sample-apps/README.md).

The image uses the [COVESA vsomeip](https://github.com/COVESA/vsomeip)
implementation of SOME/IP as [packaged in
Fedora](https://src.fedoraproject.org/rpms/vsomeip3/tree/rawhide). In
particular, the image starts the vsomeip routing manager
(non-contained), using systemd socket activation with a custom
[SELinux
policy](https://src.fedoraproject.org/rpms/vsomeip3/blob/rawhide/f/vsomeip.te)
that controls access.

After boot there are two container-based systemd services running,
`radio.service` and `engine.service`, which are running the two sample
services.

To test the image, log in and run the `radio-client` tool from a
terminal. In addition you can check the status of the services with
systemctl and journalctl.

To build the sample image (on x86) into a qemu image you can do:

```
$ cd osbuild-manifests
$ make cs9-qemu-container-regular.x86_64.qcow2
```

Then boot the image in a VM and try some of these commands:

```
# radio-client
# systemctl status radio.service
# systemctl status engine.service
# systemctl status routingmanagerd.service
# journalctrl -f
```

## Technical details

### Embedding container images

OSBuild (which is used to build the images) allows embedding
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

### Running containers from systemd

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

As an example of a quadlet container file, here is the [radio service
config](https://gitlab.com/redhat/automotive/automotive-sig/-/blob/someip-samples/osbuild-manifests/files/radio.container).
