# Building Images

The Automotive SIG uses [OSBuild](https://www.osbuild.org/) as the tool to build
its images on CentOS Stream, Fedora, or RHEL hosts, with the option to build immutable images using [OSTree](https://ostreedev.github.io/ostree/introduction/).

!!! note

    For all hosts, installing `osbuild-tools` provides the `osbuild-mpp` utility.

## Prerequisites

- **No cross-compilation**: If you want to build
  AArch64 or x86_64 images, run OSBuild on those respective systems. If you do not have access those systems, you can run OSBuild and create image
  on a Raspberry Pi 4 system. It's slower than a more powerful system, but it
  works fine.
  For instructions, see [CentOS-Stream system running on a
  Raspberry Pi 4](centos_stream_pi4.md).

- **A subscribed RHEL system**: Because building RHEL images requires access to the
  RHEL repos for access to the entitlements, RHEL images
  can only be built on a subscribed RHEL system.

## Setting up your system

### On a CentOS Stream host

1. Install OSBuild.

     ```
     dnf copr enable @osbuild/osbuild
     sed -i -e 's|baseurl=https://download.copr.fedorainfracloud.org/results/@osbuild/osbuild/epel-8-$basearch/|baseurl=https://download.copr.fedorainfracloud.org/results/@osbuild/osbuild/centos-stream-8-$basearch/|' /etc/yum.repos.d/_copr\:copr.fedorainfracloud.org\:group_osbuild\:osbuild.repo
     dnf install osbuild osbuild-tools osbuild-ostree
     ```


### On a Fedora host

1. Install OSBuild.

     ```
     dnf copr enable @osbuild/osbuild
     dnf install osbuild osbuild-tools osbuild-ostree
     ```


### On a RHEL host

1. Install OSBuild.

     ```
     dnf copr enable @osbuild/osbuild
     dnf install osbuild osbuild-tools osbuild-ostree
     ```


## Finding the manifest of interest

All the manifests are present on the project hosted at: https://gitlab.com/redhat/automotive/automotive-sig.

To download them all at once, run `git clone`.

```
git clone https://gitlab.com/redhat/automotive/automotive-sig.git
```

Once cloned, you can find the manifests under the `osbuild-manifest` folder.
They are organized by OS, then target platform. For example:
```
    osbuild-manifests
    └── cs9
        ├── cs9-build-aarch64.mpp.yml
        ├── cs9-build-x86_64.mpp.yml
        ├── qemu
        │   ├── minimal.mpp.yml
        │   └── neptune.mpp.yml
        └── rpi4
            ├── rpi4-minimal.mpp.yml
            └── rpi4-neptune.mpp.yml
```

Each folder may include a `README` file with more information
about the differences between the files.

## Building the image

Building an image is a two step process. First the selected yaml
manifest, among with some options are passed to the `osbuild-mpp`
tool. This will apply all the options and resolve all the package
names against the repositories used, producing a json manifest with a
fully resolved versions of all the packages. This json file is fully
self containerd and produces reproducible builds.

The manifest have multiple options that can affect how the manifest is
preprocessed. For example, there is an image_type variable that allows
you to specify if you want an ostree or a rpm based system. There is also
an extra_rpms variable that allows you to pass in some extra rpms that
should be added to the built image.

After preprocessing, the resolved manifest is passed to `osbuild` which
builds the final image in a set of step. When running `osbuild`
you can chose which stage(s) to export. Typically we export either the
step called "image", or the one called "qcow2". The first being a
raw image which can be written to disk, and the second being a format
used by qemu for image files.

To avoid the need to manually do the above work the `osbuild-manifest`
directory contains a Makefile that allows you to easily build the
images. To use this, just run `make` from this directory with the
right image name as target. For example:

```
[osbuild-manifests]$ make cs9-minimal-ostree.qcow2
```

This will preprocess and build the manifest for the current
architecture, defining the image type to be ostree. The resultant file
will be called `cs9-minimal-ostree.qcow2` and stored in the current
directory. Note that the makefile uses sudo, so you may be asked for
your password during the build.

If you instead want to build a raw image you can do:

```
[osbuild-manifests]$ make cs9-minimal-ostree.img
```

The full list of images available for the current architecture is available
if you run "make help".

You can use the `DEFINES` variable to override variables in the manifest. For
example, to add some extra packages, use:

```
[osbuild-manifests]$ make cs9-minimal-regular.qcow2 DEFINES='extra_rpms=["gdb","strace"]'
```

During the build, all the files are created in the `_build`
directory. This contains all the generated json files, downloaded
files (such as rpms) and cached parts of the build from previous
builds. You can remove this directory at any time to regain disk
space, as everything in this directory is derived from other sources.


## Running the image

You can either run the image in qemu/kvm or flash the image onto an SD card.

      * To boot the image in qemu/kvm, boot the qcow2 image in `virt-manager` or run it
      directly through `qemu`. For example:

        ```
        qemu-system-x86_64 \
            -machine q35 \
            -enable-kvm \
            -snapshot \
            -m 2048 \
            -drive file=image_output/qcow2/disk.qcow2 \
            -device virtio-net-pci,netdev=n0,mac=FE:45:5b:75:69:d5 \
            -netdev user,id=n0,net=10.0.2.0/24,hostfwd=tcp::2222-:22
        ```

       * To flash the image onto an SD card, run the following command:

        !!! important

            Change the block device, shown as _``/dev/sda``_ in the following example, according to your system.

        ```
        dd if=image_output/image/disk.img of=/dev/sda status=progress bs=4M
        ```

## Going further

To go further, review these other docs:

* [Updating an OSTree-based image](updating_ostree.md)
* [Customizing your OSBuild template](customize_template.md)
