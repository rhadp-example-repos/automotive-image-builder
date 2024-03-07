#!/bin/bash

set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 0
fi

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

cd "$SCRIPTPATH"

podman run -v "$PWD":"$PWD" --rm --privileged --pull=newer --security-opt label=type:unconfined_t quay.io/centos-sig-automotive/automotive-osbuild /bin/bash -c "cd $PWD/osbuild-manifests/; make $@"

