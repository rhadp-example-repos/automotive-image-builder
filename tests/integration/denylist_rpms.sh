source $TESTDIR/test-lib

cat <<EOF >test.aib.yml
name: denylist_rpms
kernel:
  remove_modules:
    - nfs
EOF

build --export tar --extend-define tar_paths='usr/lib/modules' test.aib.yml out.tar

list_tar_modules out.tar > modules.list

# nfs should have been removed
assert_file_doesnt_have_content modules.list "^nfs$"
# nfsv3 which depends on nfd should have been removed
assert_file_doesnt_have_content modules.list "^nfsv3$"
