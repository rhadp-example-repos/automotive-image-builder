# Welcome to the Automotive SIG

This is the on-going documentation for the Automotive SIG. It contains receipes
for building the images, information on how to download them as well as references
on how the SIG works.

If you are curious about the SIG's charter, members or goal, you will be able to
find this information on the
[Automotive SIG page on the CentOS wiki](https://wiki.centos.org/SpecialInterestGroup/Automotive).


## Contact points

* The CentOS-Automotive-SIG mailing list:
  <https://lists.centos.org/mailman/listinfo/centos-automotive-sig>
* The IRC channel: `#centos-automotive` on `irc.libera.chat` (More information
  on <https://libera.chat/>)
* Monthly meetings on the third Thursday, 1500 UTC, or as decided by the group


## Artifacts

Currently the SIG has manifests for different Operating Systems and platforms.
You can find them in the `osbuild-manifests` folder using the following
structure:
```
    osbuild-manifests/
    └── <OS>
        └── <platform>
```

For example:
```
    osbuild-manifests
    └── cs8
        ├── cs8-build-aarch64.mpp.json
        ├── cs8-build-x86_64.mpp.json
        ├── qemu
        │   └── neptune.mpp.json
        └── rpi4
            └── neptune-tianocore.mpp.json
```

Each of these manifests can be built using [osbuild](https://www.osbuild.org/).
The instructions are available under the `Building Images` section of the menu
in the top bar.
