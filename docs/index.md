# Welcome to the Automotive SIG

This site contains general information about the Automotive SIG, as well as
how to contribute to the repository and how to build and download images.

For more information about the SIG's charter, members, or goal, see the
[Automotive SIG page on the CentOS wiki](https://wiki.centos.org/SpecialInterestGroup/Automotive).


## Artifacts

The Automotive SIG is working on several artifacts, including:

* The Automotive Stream Distribution: This project is a binary
  distribution developed within the SIG that serves as a public,
  in-development preview of the upcoming Red Hat In-Vehicle
  Operating System.
* The Automotive SIG repositories: These are RPM repositories produced
  by the SIG to enhance the Automotive Stream Distribution.
  New packages or features can be developed and hosted there to
  expand the capabilities of the Automotive Stream Distribution.
* Sample images: These are images built with [OSBuild](https://www.osbuild.org/)
  using packages from the Automotive Stream Distribution,
  the Automotive SIG repositories, or other sources. They are
  examples of how the Red Hat automotive product can be used.

### Automotive Stream Distribution

The Automotive Stream Distribution (AutoSD) is an upstream repository
to the Red Hat automotive product, much like CentOS Stream is to RHEL.
AutoSD will be based on CentOS Stream with a few divergences.

The first divergence will be the Linux kernel. AutoSD will
rely on the kernel-automotive package rather than the CentOS
Stream kernel package.

![Automotive Stream Distribution vs CentOS Stream](img/AutoSD_CS.jpg)

As a binary distribution, AutoSD will be the place where the
community, customers, and partners can see what will land in
the automotive product. Like CentOS Stream, AutoSD will
be open to contributions using similar mechanisms.

For more information about how the content of the AutoSD
is gathered, see [Content Definition](content_definition.md).

You can browse the latest version of the Automotive Stream Distribution at:
[http://autosd.sig.centos.org](http://autosd.sig.centos.org).

You can also download a local copy of this repository using `wget`:

```
wget --recursive --no-parent -R "index.html*" 'http://autosd.sig.centos.org/AutoSD-9/latest/cs9/'
```

You must have at least 1.3G of available disk space to accommodate
both aarch64 and x86_64. The disk space requirement is subject to
change as the package set evolves.

### The Automotive SIG repositories

You can browse the Automotive SIG repositories at:
[https://buildlogs.centos.org/9-stream/automotive/](https://buildlogs.centos.org/9-stream/automotive/).

The Automotive SIG repositories include packages that are not
necessarily part of the Red Hat automotive offering, but which
may be interesting to SIG members. These packages might be works
in progress that could land in the AutoSD or the Red Hat automotive
offering. The packages could also be purely experimental, for research and
development, or integration work that remains outside of the AutoSD.

All SIG members can request packages to be distributed through these
repositories as long as they meet [CentOS requirements for SIG](https://wiki.centos.org/SpecialInterestGroup#Requirements).


### Sample images

The [Automotive SIG](https://gitlab.com/redhat/automotive/automotive-sig)
repository contains manifests for different operating systems and platforms.

The manifests are located in the `osbuild-manifests` folder.
```
    osbuild-manifests/
    └── <OS>
        └── <platform>
```

For example:
```
    osbuild-manifests
    └── cs9
        ├── minimal.mpp.yml
        ├── neptune.mpp.yml
        └── ...
```

You can use [OSBuild](https://www.osbuild.org/) to build each of these manifests.
For more information, see [Building images](building/index.md).

You can also find pre-built images from our [Download images
](download_images.md) page.


## Contact points

* [CentOS-Automotive-SIG mailing list](https://lists.centos.org/mailman/listinfo/centos-automotive-sig)
* IRC channel: `#centos-automotive` on `irc.libera.chat`. For more information, see [Libera.Chat](https://libera.chat/>).
