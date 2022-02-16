# Building Images

The Automotive SIG uses [OSBuild](https://www.osbuild.org/) as the tool to build
its images on CentOS Stream, Fedora, and RHEL hosts, with the option to build immutable images using [OSTree](https://ostreedev.github.io/ostree/introduction/).

!!! note

    For all hosts, installing `osbuild-tools` provides the `osbuild-mpp` utility.

## Prerequisites

- **No cross-compilation**: To build AArch64 or x86_64 images, you must run OSBuild on the respective systems. If you do not have access those systems, run OSBuild and create an image on a Raspberry Pi 4 system. This method is slower than a more powerful system, but it works. For more information, see [CentOS-Stream system running on a Raspberry Pi 4](centos_stream_pi4.md).

- **A subscribed RHEL system**: To build RHEL images, you must have access to a subscribed RHEL system in order to access to the entitlements. RHEL images can only be built on subscribed RHEL systems.

## Installing osbuild

To configure your system you must install osbuild and the related tools. We use a newer version of these tools than what is generally available in the distributions, so you must configure a custom repository.

## Using make manifests

1. Enable the osbuild repo:
```
dnf copr enable @osbuild/osbuild
```
2. Update the `baseurl` variable:
```
sed -i -e 's|baseurl=https://download.copr.fedorainfracloud.org/results/@osbuild/osbuild/epel-8-$basearch/|baseurl=https://download.copr.fedorainfracloud.org/results/@osbuild/osbuild/centos-stream-8-$basearch/|' /etc/yum.repos.d/_copr\:copr.fedorainfracloud.org\:group_osbuild\:osbuild.repo
```
3. Install osbuild and related packages:
```
dnf install osbuild osbuild-tools osbuild-ostree
```

### Installing osbuild on CentOS Stream 9, Fedora, or RHEL

1. Enable the osbuild repo:
```
dnf copr enable @osbuild/osbuild
```
2. Install osbuild and related packages:
```
dnf install osbuild osbuild-tools osbuild-ostree
```

## Finding a manifest

All manifests exist in the project hosted at the [Automotive SIG GitLab](https://gitlab.com/redhat/automotive/automotive-sig).

1. Clone the repository to download all manifests:
```
git clone https://gitlab.com/redhat/automotive/automotive-sig.git
```
2. Locate the manifests in the `osbuild-manifest` folder. Manifests are organized by OS, then by target platform. For example:
```
    osbuild-manifests
    └── cs9
        ├── minimal.mpp.yml
        └   neptune.mpp.yml
```
Each folder may include a `README` file with information about the differences between the files.

## Building the image

You can build an image manually or by using makefile.

### Building the image manually

Building an image manually is a two-step process.

1. Pass the selected YAML manifest and some options to the `osbuild-mpp` tool.

 This applies the options and resolves the package names against the repositories used to produce a JSON manifest with fully resolved versions of all the packages. This JSON file is fully self contained and produces reproducible builds.

 The manifest has multiple options that can affect how the manifest is preprocessed, for example:

      * `image_type` specifies whether the system is `ostree` or `dnf` based.
      * `extra_rpms` passes extra RPMs to the built image.

2. After preprocessing, pass the resolved manifest to osbuild, which builds the image in a series of steps.

 When you run osbuild you can choose which steps to export. Typically, we export either the step called _image_ or the step called _qcow2_:

      * Image is a raw image that can be written to disk.
      * QCOW2 is a format used by QEMU for image files.

### Using makefile to build the image

You can simplify the build process by using makefile.

!!! note

     Makefile uses sudo, so you may be asked for your password during the build process.

1. From the `osbuild-manifest` directory, run `make`. Be sure to use the correct image name as the target:
```
make cs9-qemu-minimal-ostree.x86_64.qcow2
```
 This command preprocesses and builds the manifest for the current architecture and defines the image type to be `ostree`. This results in a file named `cs9-qemu-minimal-ostree.x86_64.qcow2`, which is stored in the current directory.

2. You can use makefile to build RAW images as well. To see the full list of images available for the current architecture:
```
make help
```
3. Optional: Remove the `_build` directory to regain disk space:
```
rm -r _build
```
!!! note

    During the build process, artifacts such as JSON files, RPMs, and cached parts from previous builds are stored in the `_build` directory. Everything in this directory is derived from other sources.

### Changing the default password

The sample images use `password` as the default password for `root` and `guest`. You can change the default password when you build the image:
```
DEFINES='root_password="hash_of_new_password"'
```

## Running the image
You can either run the image in QEMU/KVM or flash the image onto an SD card.

### Booting the image in QEMU/KVM

1. Boot the QCOW2 image in `virt-manager` or run it directly through QEMU:

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
2. For `qemu-system-x86_64` target, add this QEMU command line option to enable booting with UEFI:

```
-bios /usr/share/OVMF/OVMF_CODE.fd
```

### Flashing the image onto an SD card

To flash the image onto an SD card:

```
dd if=cs9-qemu-minimal-regular.x86_64.img of=/dev/sda status=progress bs=4M
```
!!! important

    In the example, the block device is called /dev/sda. You must change this to match the block device used in your system. If required, add `-bios /usr/share/OVMF/OVMF_CODE.fd` to QEMU command.

## Overriding variables

You can use the `DEFINES` variable to override variables in the manifest. This variable contains a space-separated list of items in `variable=json-data` form.

To add extra packages:

```
make cs9-qemu-minimal-regular.x86_64.qcow2 DEFINES='extra_rpms=["gdb","strace"]'
```

Some variables you might want to override include:
* `arch`: The architecture to resolve against; allows preprocessing
    against a non-native architecture.
* `cs9_baseurl`: The base URL of the CentOS 9 repo; can be overridden to use a local mirror.
* `extra_rpms`: List of additional RPMs installed in most images;  defaults to empty.
* `image_size`: The total size of the disk image.
* `kernel_rpm`: The name of the kernel package used; defaults to `kernel-auto`.
* `ostree_ref`: The name used for the ref when you commit to an `ostree` repo.
* `display_server`: The name of the display server (wayland or xorg); defaults to wayland.
* `static_uuids`: Set to true to use static default uuids for fileystems rather than generated

## Using `make manifests`

You can use `make manifests` to preprocess all of the existing manifests without building them. You can use `make manifests` to verify that all combinations of options still work after a change or to inspect the resulting manifests.

In addition to the image types `*.img` and `*.qcow2`, the makefile also supports targets such as:
* `*.rootfs`
* `*.repo`
* `*.tar`
* `*.container`
* `*.ext4`

These targets are useful during development and testing. For more information, run `make help`.

## Building in a virtual machine

The makefile configuration supports running osbuild inside a virtual machine. There are two scenarios in which this is beneficial:
* Standard osbuild requires root/sudo permissions, because it performs some system-level operations such as loopback mounts. Running osbuild in a VM allows you to run it non-privileged.
* When you build an image for a different architecture, you can use QEMU software emulation to make this work. Software emulation is slower than native, but for some use cases it is sufficient.

Running `make osbuildvm-images` uses osbuild on the host to build the supporting image files, `_build/osbuildvm-*`, which are required to build an image on a VM. The supporting image files can later be used to build other images from the same architecture inside a virtual machine by passing `VM=1` to `make`.

To build images from a different architecture you must copy the output of `osbuildvm-images` from a build on a different architecture into `_build`. Then run `make` with a target that has a different architecture, for example, `make cs9-qemu-minimal-regular.aarch64.qcow2`.

!!! note

     If you have a previous version of `osbuildvm-images` for a different architecture, you can rebuild or refresh them by using `VM=1` on your architecture.

## Additional resources

For more information, see:

* [Updating an OSTree-based image](updating_ostree.md)
* [Customizing your OSBuild template](customize_template.md)
