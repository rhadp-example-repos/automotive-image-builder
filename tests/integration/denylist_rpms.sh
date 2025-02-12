source $TESTDIR/test-lib

cat <<EOF >test.aib.yml
name: denylist_rpms
content:
  rpms:
    - strace
EOF

if trybuild --export rpmlist --extend-define denylist_rpms=strace test.aib.yml out.json 2> error.txt; then
    fatal should not have succeeded build with denied rpm
fi
assert_file_has_content error.txt "Rootfs contains denied rpms"
