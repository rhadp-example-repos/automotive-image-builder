#!/bin/bash

set -e

usage() {
    echo "Usage:"
    echo "  auto-image-builder.sh [OPTION...] MAKE_ARGS"
    echo
    echo "Options:"
    echo "  -h,--help                - Display usage"
    echo "  -n,--nopull              - Don't attempt to pull new image"
    echo
}

PULL_ARG="--pull=newer"
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      usage
      exit 0
      ;;
    -n|--nopull)
      PULL_ARG=
      shift 1
      ;;
    *)
      break;
      ;;
  esac
done

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 0
fi

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

cd "$SCRIPTPATH"

podman run -v "$PWD":"$PWD" --rm --privileged $PULL_ARG --security-opt label=type:unconfined_t quay.io/centos-sig-automotive/automotive-osbuild /bin/bash -c "cd $PWD/osbuild-manifests/; make $@"

