source $TESTDIR/test-lib

cat <<EOF >test.aib.yml
name: install_rpms
content:
  rpms:
    - strace
qm:
  content:
     rpms:
      - less
EOF

build --export rpmlist test.aib.yml out.json

cat out.json | jq '.rootfs|has("strace")' > has_strace.txt
assert_file_has_content has_strace.txt true

cat out.json | jq '.qm_rootfs_base|has("less")' > qm_has_less.txt
assert_file_has_content qm_has_less.txt true
