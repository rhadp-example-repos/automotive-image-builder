# Building Images

The Automotive SIG is using [osbuild](https://www.osbuild.org/) as tool to build
its images.

## Pre-requisite

This offers a lot of flexibility but has, of course, a few requirements you need
to be aware of:

- **No cross-compilation**: This is a principle that Red Hat has followed for years
  and which thus cascades down in its ways of working. So if you want to build
  an aarch64 images, you will need to run osbuild on aarch64.

- **Building a RHEL image**: Since building RHEL images will need access to the
  RHEL repos, it will need access to the entitlements, so building RHEL images
  can only be done on a subscribed RHEL system.

As described on above you need to run osbuild on aarch64 system to build an aarch64
image. If you do not have access to a better one, you can run osbuild and create image
on a Raspberry Pi 4 system, it will be slower than a more powerful system, but it
works fine.
You can find here instructions on how to get a [CentOS-Stream system running on a
Raspberry Pi 4](centos_stream_pi4.md)


## Setting up your system

### On a CentOS-Stream host

* Install osbuild

```
dnf copr enable @osbuild/osbuild
sed -i -e 's|baseurl=https://download.copr.fedorainfracloud.org/results/@osbuild/osbuild/epel-8-$basearch/|baseurl=https://download.copr.fedorainfracloud.org/results/@osbuild/osbuild/centos-stream-8-$basearch/|' /etc/yum.repos.d/_copr\:copr.fedorainfracloud.org\:group_osbuild\:osbuild.repo
dnf install osbuild osbuild-tools
```

`osbuild-tools` contains the `osbuild-mpp` utility.

* **Optional**: to build OStree-based images:

```
dnf install osbuild-ostree
```

### On a Fedora host

* Install osbuild

```
dnf copr enable @osbuild/osbuild
dnf install osbuild osbuild-tools
```

`osbuild-tools` contains the `osbuild-mpp` utility.

* **Optional**: to build OStree-based images:

```
dnf install osbuild-ostree
```

### On a RHEL host

* Install osbuild

```
dnf copr enable @osbuild/osbuild
dnf install osbuild osbuild-tools
```

`osbuild-tools` contains the `osbuild-mpp` utility.


* **Optional**: to build OStree-based images:

```
dnf install osbuild-ostree
```


## Finding the manifest of interest

All the manifests are present on the project hosted at: https://gitlab.com/redhat/automotive/automotive-sig

You can thus download them all at once by doing:

```
git clone https://gitlab.com/redhat/automotive/automotive-sig.git
```

Once cloned, you can find the manifests under the `osbuild-manifest` folder.
They are organized by OS, then target platform.


For example:
```
    osbuild-manifests
    └── cs8
        ├── cs8-build-aarch64.mpp.json
        ├── cs8-build-x86_64.mpp.json
        ├── qemu
        │   ├── minimal.mpp.json
        │   └── neptune.mpp.json
        └── rpi4
            └── neptune-tianocore.mpp.json
```

Each folder may, in addition, include a `README` file with more information
about the differences between the files present.


## Building the image

Once you have selected an image to build, you will have to preprocess the
template manifest with the `osbuild-mpp` script and then actually build the
image with `osbuild`.

In the following example, we will be building a basic CentOS-Stream 8 image
targetting the Raspberry Pi 4 platform.


#### Pre-compile the template

```
osbuild-mpp osbuild-manifests/cs8/rpi4/neptune-tianocore.mpp.json cs8-rpi4.json
```

By default the generated manifes is based on ostree, but you can also
create a non-ostree image if you pass `-D image_type=\"regular\"` to
osbuild-mpp.

#### Build the image

The basic command is:
```
osbuild \
    --store <where to store intermediary outputs> \
    --output-directory <where to store outputs> \
    --export <name of pipeline to export> \
    <pre-processed osbuild manifest>
```

Below are two examples of the command you can run depending on the type of image
you wish to build.

- Building a raw image

If you wish to build a raw image that can then be flashed upon a SD card to boot
a board, you can create the image via:
```
osbuild --store osbuild_store --output-directory image_output  --export image cs8-rpi4.json
```

- Building a qcow2 image

If you wish to build a qcow2 image that can then be booted as a Virtual Machine,
you can create it via:
```
osbuild --store osbuild_store --output-directory image_output  --export qcow2 cs8-rpi4.json
```

#### Running the image

Once the image is created you can either:

- Boot the image in qemu/kvm

To do this, you can simply boot the qcow2 image in `virt-manager` or run it
directly via `qemu`.

For example:
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

- Flash the image onto an SD card

**/!\\** Beware to change the block device (``/dev/sda`` below) according to your system.

```
dd if=image_output/image/disk.img of=/dev/sda status=progress bs=4M
```


## Going further

If you wish to go further, do not hesitate to check out our docs:

* [Updating an OStree-based image](updating_ostree.md)
* [Customizing your osbuild template](customize_template.md)
