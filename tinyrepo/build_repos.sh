#!/bin/bash

d=`date "+%Y%m%d"`
AUTOSIGREPO=$1
HTMLROOT=$2

python $AUTOSIGREPO/tinyrepo/initiate_repo.py \
    $HTMLROOT/cs9-stream/ \
    --pkgslist=$HTMLROOT/cs9-stream/pkgslist_$d

for arch in aarch64 x86_64
do
  mkdir -p $HTMLROOT/cs9-stream/$arch/$d
  pushd $HTMLROOT/cs9-stream/$arch/$d
  createrepo_c ../packages/ -o . -i ../../pkgslist_$d
  popd

  # Update the `latest` symlink
  ln -nsf $d $HTMLROOT/cs9-stream/$arch/latest
done
