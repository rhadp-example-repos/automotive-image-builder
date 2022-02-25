# Welcome to the Automotive SIG

This site contains general information about the Automotive SIG, as well as 
how to contribute to the repository and how to build and download images.

For more information about the SIG's charter, members, or goal, see the
[Automotive SIG page on the CentOS wiki](https://wiki.centos.org/SpecialInterestGroup/Automotive).


## Contact points

* [CentOS-Automotive-SIG mailing list](https://lists.centos.org/mailman/listinfo/centos-automotive-sig)
* IRC channel: `#centos-automotive` on `irc.libera.chat`. For more information, see [Libera.Chat](https://libera.chat/>).


## Manifests

The SIG repository contains manifests for different operating systems and platforms.

The [latest product build](http://54.247.135.67) is defined by the manifests on the 
main branch, which is based on the latest successful build from automotive-sig/main. 
It contains RPMs for aarch64 and x86_64 from Appstream, BaseOS, and CRB.

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
        └── neptune.mpp.yml
```

You can use [OSBuild](https://www.osbuild.org/) to build each of these manifests. 
For more information, see [Building images](https://sigs.centos.org/automotive/building/).
