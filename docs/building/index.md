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
    ├── cs8
    │   ├── cs8-build-aarch64.mpp.json
    │   ├── cs8-build-x86_64.mpp.json
    │   ├── qemu
    │   │   ├── minimal.mpp.json
    │   │   └── neptune.mpp.json
    │   └── rpi4
    │       ├── rpi4-minimal.mpp.json
    │       └── rpi4-neptune.mpp.json
    └── cs9
        ├── cs9-build-aarch64.mpp.json
        ├── cs9-build-x86_64.mpp.json
        ├── qemu
        │   ├── minimal.mpp.json
        │   └── neptune.mpp.json
        └── rpi4
            ├── rpi4-minimal.mpp.json
            └── rpi4-neptune.mpp.json
```

Each folder may include a `README` file with more information
about the differences between the files.

## Building the image

Once you select an image to build, you must preprocess the
template manifest with the `osbuild-mpp` script and then build the
image with OSBuild.

The following example builds a basic CentOS-Stream 8 image
targeting the Raspberry Pi 4 platform.

1. Precompile the template.

    ```
    osbuild-mpp osbuild-manifests/cs8/rpi4/rpi4-neptune.mpp.json cs8-rpi4.json
    ```

    !!! note

        By default, the generated manifest is based on OSTree, but you can also create a non-OSTree image if you pass `-D image_type=\"regular\"` to `osbuild-mpp`.

1. Either build a raw image or a qcow2 image.

     ```
     osbuild \
         --store <where to store intermediary outputs> \
         --output-directory <where to store outputs> \
         --export <name of pipeline to export> \
         <pre-processed osbuild manifest>
     ```

       1. To build a raw image that you can then flash upon an SD card to boot
    a board, run the following command:

        ```
        osbuild \
        --store osbuild_store \
        --output-directory image_output \
        --export image cs8-rpi4.json
        ```

      1. To build a qcow2 image that you can then boot as a virtual machine, run the following command:

        ```
        osbuild \
        --store osbuild_store \
        --output-directory image_output \
        --export qcow2 cs8-rpi4.json
        ```

1. Either run the image in qemu/kvm or flash the image onto an SD card.

      1. To boot the image in qemu/kvm, boot the qcow2 image in `virt-manager` or run it
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

       1. To flash the image onto an SD card, run the following command:

        !!! important

            Change the block device, shown as _``/dev/sda``_ in the following example, according to your system.

        ```
        dd if=image_output/image/disk.img of=/dev/sda status=progress bs=4M
        ```

## Going further

To go further, review these other docs:

* [Updating an OSTree-based image](updating_ostree.md)
* [Customizing your OSBuild template](customize_template.md)
