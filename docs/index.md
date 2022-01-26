# Welcome to the Automotive SIG

This is the documentation for the Automotive SIG. It contains instructions
about how to build and download images and information about how
the SIG works.

For more information about the SIG's charter, members, or goal, see the
[Automotive SIG page on the CentOS wiki](https://wiki.centos.org/SpecialInterestGroup/Automotive).


## Contact points

* The CentOS-Automotive-SIG mailing list:
  <https://lists.centos.org/mailman/listinfo/centos-automotive-sig>
* The IRC channel: `#centos-automotive` on `irc.libera.chat` (more information
  on <https://libera.chat/>)


## Artifacts

The SIG currently has manifests for different operating systems and platforms.

The [latest product build](http://auto-product-build.s3-website-eu-west-1.amazonaws.com/latest/cs9/) is defined by the manifests on the main branch based on the latest successful build from automotive-sig/main, and it contains RPMs for aarch64 and x86_64 from Appstream, BaseOS, and CRB.

You can find them in the `osbuild-manifests` folder organized in the following
structure:
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
        └── neptune.mpp.yml
```

Each of these manifests can be built using [OSBuild](https://www.osbuild.org/).
The instructions are available on the [Building Images](https://sigs.centos.org/automotive/building/) page.
