# Automotive image builder

Automotive image builder is a tool to create various kinds of OS images based on CentOS derived
OSes. The images can support package-based mode (called "package") as well as image-based mode
(called "image").

The main tool is called `automotive-image-builder`, and the basic operation it does is called
"composing" manifests. The compose operation takes a yaml-based automotive image manifest, as well
as a set of options affecting the compose and resolves the manifest into an osbuild json file. This
json file is a precise build instruction for how to build an image with osbuild with the very
specific software that was chosen during the compose. For example, the version of selected packages
and container images is chosen during the compose.

For example, to build a qcow2 image you can run:

```shell
 $ automotive-image-builder compose --distro cs9 --mode package --target qemu my-image.mpp.yml osbuild.json
 $ sudo osbuild --store osbuild_store --output-directory output --export qcow2 osbuild.json
```

You can also combine these two in one command:

```shell
 $ automotive-image-builder build --distro cs9 --mode package --target qemu --export qcow2 my-image.mpp.yml osbuild.json
```

These will first compose the osbuild.json file, and then build it and export the "qcow2" output,
which will end up in the "output" directory (in particular as `output/qcow2/disk.qcow2`). You an then
run it using:

```shell
 $ automotive-image-runner  output/qcow2/disk.qcow2
```

The sample-images repository (https://gitlab.com/CentOS/automotive/sample-images) has a lot of
example images, as well as some tools that makes it easy to build those images.

## Controlling the image built

When composing (or building) a manifest there are some core options that control what gets built:

* `--arch`: The hardware architecture to build for (`x86_64` or `aarch64`). If not specified the native
   architecture is used. Note: It is possible to compose an image for any architecture, but you can
   only build one for the native architecture.

* `--target`: The board to target, defaults to `qemu`. You can get a list of the supported targets from
 `automotive-image-builder list-targets`.

* `--mode`: Either "`package`" or "`image`". Default is `image`. Package mode is a read-write OS based on
  dnf to install package. Image mode is an immutable OS image based on ostree that supports
  atomically updates, but no modification on the package level. Image mode is meant to be used in
  production, but package mode is more useful when doing development and testing.

* `--distro`: There are a set of distribution definitions that can be used. These define what package
  repositories to use. The default used in "cs9", but the full list can be gotten with
  `automotive-image-builder list-dist`.  It is also possible to extend the list of distributions
  with your custom ones by putting them in a directory called "/some/dir/distro" and passing
  `--include /some/dir` on the argument list.

Additionally, there a a variety of variables supported that modifies how the manifest works. These
can be defined either in your manifest using the "mpp-var" block at the top, or by specifying them
on the command-line like this:

* `--define VAR=VALUE`: Sets the variable to the specified value, which is a yaml value.

* `--define-file PATH`: Loads variables from a yaml dict in a file, where the keys are variable names.

* `--extend-define VAR=VALUE`: Similar to `--define`, but this is only useable for list-based variable
  and will extend the list already in the variable (or start a new list if it is unset). This
  support specifying either a list value or just a plain item value.

When the manifest has been composed, the generated osbuild json file can contain several types of
things that can be build. For example, it can generate both raw image files and qcow2 files. When
building you need to the `--export` option to select what you want to build. The available exports
are:

* `image`: A raw disk image with partitions
* `qcow2`: A qcow2 format disk image with partitions
* `ext4`: An ext4 filesystem containing just the rootfs partition (i.e. no boot partitions, etc)
* `aboot`: An android boot system partition image and a boot partition
* `container`: A container image you can run with podman or docker
* `tar`: A tar file containing the basic rootfs files
* `ostree-commit`: An ostree repo with the commit built from the image
* `ostree-oci-image`: An oci image wrapping the ostree commit from ostree-commit
* `rpmlist`: A json file listing all the rpms used in the image

## Commonly used variables

Here are some commonly used variable supported and what they mean:

* `use_qm`: If this is true, then the support for the qm partion is included in the image, see below for details
* `extra_rpms`: Many manifests (e.g. in sample-images) support this variable to add extra rpms to the image
* `image_size`: Specifies the size in bytes (as a string) of the generated image
* `use_composefs_signed`: If this is set to false, then use of ostree will not require signed commits. This can be needed in some cases if you want to modify the ostree image on the target system (e.g. layering packages).
* `use_transient_etc`: If this is set to false, then changes to `/etc` will be persisted over boot on image based builds. This is not recommended in production, but can be useful during testing.
* `use_static_ip`: If this is set, then NetworkManager is not used and the below set of options specify the hardcoded network config:
* `static_ip`: The ip address
* `static_gw`: The default gateway ip
* `static_dns`: The dns server ip
* `static_ip_iface`: The network interface name
* `static_ip_module`: The network driver kernel module to load (if any)
* `use_debug`: If set to true, a lot more debugging info will be shown during boot

## Manifests

A manifest is a yaml file that describes a set of pipelines. Each pipeline is a set of stages that
are run in order to produce a result. The input to each stage can depend on the output of other
pipelines. When building a manifest the "export" option defines what pipeline (and its dependencies)
to build.

The most basic pipeline that all end user manifest need to supply is called "rootfs" and contains
stages that set up the basic content of the image. These typically start with installing a set of
rpm packages, and then doing some additional steps like enabling systemd units, creating users and
installing containers.

On top of the rootfs pipeline, `automotive-image-builder` adds its own standard pipelines that are
used during the build. These includes the final pipelines that are used for the export, but also
intermediate ones as well as the "build" pipeline which is used when building the other pipelines.

Here is an example small manifest file: [example.mpp.yml](example.mpp.yml), you can build and run it it using:

```shell
$ automotive-image-builder build --export qcow2 example.mpp.yml example.qcow2
$ automotive-image-runnter example.qcow2
```


## Using qm

`automotive-image-builder` supports the [QM](https://github.com/containers/qm/tree/main) package for
isolating quality-managed code in a separate partition. When this is used, two pipelines are built,
one the regular one and for the qm partition, called `qm_rootfs`. In the final image the qm root
filesystem will be accessible under `/usr/share/qm/rootfs`.

The `qm_rootfs` pipeline must start with the contents of the automatic `qm_rootfs_base` pipeline, which
contains the basic stuff needed for the qm partion, and then it can do any further changes that are
necessary, like installing container images. This pipeline would start like this:

```yaml
- name: qm_rootfs
  build: name:build
  stages:
  - type: org.osbuild.copy
    inputs:
      tree:
        type: org.osbuild.tree
        origin: org.osbuild.pipeline
        references:
          - name:qm_rootfs_base
    options:
      paths:
        - from: input://tree/
          to: tree:///
```

Additionally, the manfest can set the `qm_extra_rpms` variable in the `mpp-vars` dict to add
additional rpms to be installed in the `qm_rootfs_base` pipeline, on top of the basic stuff
that is installed there.

## Embedding containers in images

It is possible to embed container images in the images which are automatically available to podman
in the image. To do this, you need to set the `use_containers_extra_store` variable to `true`, and
then add a stage like this to the rootfs (or `qm_rootfs`) pipeline:

```yaml
  - type: org.osbuild.skopeo
    inputs:
      images:
        type: org.osbuild.containers
        origin: org.osbuild.source
        mpp-resolve-images:
          images:
            - source: registry.gitlab.com/centos/automotive/sample-images/demo/auto-apps
              tag: latest
              name: localhost/auto-apps
    options:
      destination:
        type: containers-storage
        storage-path:
          mpp-eval: containers_extra_store
```

This can then be run from the image. We recommend using a [quadlet
.container](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) file to start the
container from systemd. One can be installed like this:

```yaml
  - type: org.osbuild.copy
    inputs:
      inlinefile1:
        type: org.osbuild.files
        origin: org.osbuild.source
        mpp-embed:
          id: example.container
          path: files/example.container
    options:
      paths:
      - from:
          mpp-format-string: input://inlinefile1/{embedded[example.container']}
        to: tree:///etc/containers/systemd/example.container
```
