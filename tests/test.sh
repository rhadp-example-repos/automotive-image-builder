#!/usr/bin/bash

set -e

for arch in x86_64 aarch64; do
    for it in regular ostree; do
        for target in qemu ridesx4 ; do
            for def in "" use_qm=true use_aboot=true ; do
                if [ "$def" != "" ]; then
                   def_arg="--define $def"
                else
                    def_arg=""
                fi
                echo composing --arch $arch --target $target --image-type $it $def_arg
                ./automotive-image-builder compose --arch $arch --target $target --image-type $it $def_arg tests/test.mpp.yml _test.json
            done
        done
    done
done
rm _test.json
