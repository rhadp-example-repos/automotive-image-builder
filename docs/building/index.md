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

## Installing osbuild

To set up your system you need to install osbuild and the related
tools.  We are using a newer version of these tools than what is
generally available in the distributions, so a custom repository must
be configured.

### On a CentOS 8 Stream host

```
dnf copr enable @osbuild/osbuild
sed -i -e 's|baseurl=https://download.copr.fedorainfracloud.org/results/@osbuild/osbuild/epel-8-$basearch/|baseurl=https://download.copr.fedorainfracloud.org/results/@osbuild/osbuild/centos-stream-8-$basearch/|' /etc/yum.repos.d/_copr\:copr.fedorainfracloud.org\:group_osbuild\:osbuild.repo
dnf install osbuild osbuild-tools osbuild-ostree
```


### On a Fedora host

```
dnf copr enable @osbuild/osbuild
dnf install osbuild osbuild-tools osbuild-ostree
```


### On a RHEL host

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
        ├── minimal.mpp.yml
        └   neptune.mpp.yml
```

Each folder may include a `README` file with more information
about the differences between the files.

## Building the image

Building an image is a two step process. First the selected yaml
manifest, among with some options are passed to the `osbuild-mpp`
tool. This will apply all the options and resolve all the package
names against the repositories used, producing a json manifest with
fully resolved versions of all the packages. This json file is fully
self contained and produces reproducible builds.

The manifest have multiple options that can affect how the manifest is
preprocessed. For example, there is an `image_type` variable that
allows you to specify if you want an ostree or a dnf based
system. There is also an `extra_rpms` variable that allows you to pass
in extra rpms that should be added to the built image.

After preprocessing, the resolved manifest is passed to `osbuild`
which builds the image in a series of steps. When running `osbuild`
you can chose which step(s) to export. Typically we export either the
step called "image", or the one called "qcow2". The first being a raw
image which can be written to disk, and the second being a format used
by qemu for image files.

To avoid the need to manually do the above work the `osbuild-manifest`
directory contains a Makefile that allows you to easily build the
images. To use this, just run `make` from this directory with the
right image name as target. For example:

```
make cs9-qemu-minimal-ostree.x86_64.qcow2
```

This will preprocess and build the manifest for the current
architecture, defining the image type to be ostree. The resultant file
will be called `cs9-qemu-minimal-ostree.x86_64.qcow2` and stored in the current
directory. Note that the makefile uses sudo, so you may be asked for
your password during the build.

If you instead want to build a raw image you can do:

```
make cs9-qemu-minimal-ostree.x86_64.img
```

The full list of images available for the current architecture is available
if you run "make help".

During the build, all the files are created in the `_build`
directory. This contains all the generated json files, downloaded
files (such as rpms) and cached parts of the build from previous
builds. You can remove this directory at any time to regain disk
space, as everything in this directory is derived from other sources.


## Running the image

You can either run the image in qemu/kvm or flash the image onto an SD card.

To boot the image in qemu/kvm, boot the qcow2 image in `virt-manager` or run it
directly through `qemu`. For example:

```
qemu-system-x86_64 \
    -machine q35 \
    -enable-kvm \
    -snapshot \
    -m 2048 \
    -drive file=cs9-qemu-minimal-regular.x86_64.qcow2 \
    -cpu qemu64,+ssse3,+sse4.1,+sse4.2,+popcnt \
    -device virtio-net-pci,netdev=n0,mac=FE:45:5b:75:69:d5 \
    -netdev user,id=n0,net=10.0.2.0/24,hostfwd=tcp::2222-:22
```

To flash the image onto an SD card, run the following command:

!!! important

    Change the block device, shown as _``/dev/sda``_ in the following example, according to your system.
    In case needed add `-bios /usr/share/OVMF/OVMF_CODE.fd` to qemu command

```
dd if=cs9-qemu-minimal-regular.x86_64.img of=/dev/sda status=progress bs=4M
```

!!! note

    Our sample images have all a dummy password hard-coded for their `root` and
    `guest`. That password is simply: `password`.
    That default value can be overriden at build time using:
    `DEFINES='root_password="hash_of_new_password"'`


## Other features

You can use the `DEFINES` variable to override variables in the manifest. This
variable contains a space separated list items in `variable=json-data` form.
For example, to add some extra packages, use:

```
make cs9-qemu-minimal-regular.x86_64.qcow2 DEFINES='extra_rpms=["gdb","strace"]'
```

Variables that may be interesting to override are:

* `arch`: The archticture to resolve against, allows preprocessing
    against a non-native architecture.
* `cs9_baseurl`: The base url of the centos9 repo, can be overridden
    to use a local mirror.
* `extra_rpms`: List of edditional rpms installed in most images,
    defaults to empty.
* `image_size`: The total size of the disk image.
* `kernel_rpm`: The name of the kernel package used, defaults to
    `kernel-auto`.
* `ostree_ref`: Name used for the ref when commiting an ostree repo
* `display_server`: The name of the display server, wayland or xorg. Defaults to wayland.

You can use `make manifests` to pre-process all the existing manifests
without building them. This can be useful to ensure that all
combination of options still work after a change, or to inspect
the resulting manifests.

Other than the image types `*.img` and `*.qcow2` the Makefile also
supports `*.rootfs` and `*.repo` targets.  These produce as output
full directories containering the files from the rootfs, and the
ostree repo with the commit respectively. These are useful e.g. during
development and testing.

## Building in a virtual machine

The makefile setup supports running osbuild inside a virtual machine.
There are two reasons you might want to do this. First of all, regular
osbuild requires root/sudo permissions, as it does some system level
operations like loopback mounts. Running it in a VM allows you do run
it non-privileged. Secondly, if you are building an image for a
different architecture, you can use qemu software emulation to make
this work. Software emulation is slower than native, but for some
usecases it can be fast enough.

Running `make osbuildvm-images` will use osbuild on the host to build
the supporting image files (`_build/osbuildvm-*`) needed for
this. These can later be used to build other images from the same
architecture inside a virtual machine by by passing `VM=1` to make.

To build images from a different archtiecture you need to copy the
output of osbuildvm-images from a build on a different architecure into
`_build` and then just run make with a target that has a different
arch. For example `make cs9-qemu-minimal-regular.aarch64.qcow2`.

Note that if you have a previous version of the osbuildvm images for
a different arch, you can rebuild/refresh them by using `VM=1` on
your arch.

## Going further

To go further, review these other docs:

* [Updating an OSTree-based image](updating_ostree.md)
* [Customizing your OSBuild template](customize_template.md)
