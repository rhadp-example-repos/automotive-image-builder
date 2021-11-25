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
* Monthly meetings on the third Thursday at 1500 UTC, or as decided by the group


## Artifacts

The SIG currently has manifests for different operating systems and platforms.
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
