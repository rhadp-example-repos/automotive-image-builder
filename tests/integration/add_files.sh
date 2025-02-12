source $TESTDIR/test-lib

cat <<EOF >test.aib.yml
name: add_files
content:
  make_dirs:
    - path: /dir
  add_files:
    - path: /dir/file1.txt
      source_path: test.aib.yml
    - path: /dir/file2.txt
      text: |
        This is the file content
    - path: /dir/file3.txt
      url: "https://gitlab.com/CentOS/automotive/src/automotive-image-builder/-/raw/main/README.md?ref_type=heads&inline=false"

qm:
  content:
    make_dirs:
      - path: /dir
    add_files:
     - path: /dir/file4.txt
       text: |
         This is the qm file content
EOF

build --export tar --extend-define tar_paths=['dir','usr/lib/qm/rootfs/dir'] test.aib.yml out.tar

tar xvf out.tar
assert_file_has_content dir/file1.txt "name: add_files"
assert_file_has_content dir/file2.txt "This is the file content"
assert_file_has_content dir/file3.txt "Automotive image builder"
assert_file_has_content usr/lib/qm/rootfs/dir/file4.txt "This is the qm file content"
