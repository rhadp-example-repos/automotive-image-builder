#!/usr/bin/bash

set -e
TAG=$1

rm -rf osbuild-for-import
git clone --depth 1 --branch $TAG https://github.com/osbuild/osbuild.git osbuild-for-import
mkdir -p mpp/aibosbuild/util
cp -r osbuild-for-import/tools/osbuild/util/*.py mpp/aibosbuild/util

cp osbuild-for-import/tools/osbuild-mpp mpp/aib-osbuild-mpp

sed -i "s/from osbuild.util/from aibosbuild.util/" mpp/aib-osbuild-mpp mpp/aibosbuild/util/*.py

rm -rf osbuild-for-import
