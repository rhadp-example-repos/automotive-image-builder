source $TESTDIR/test-lib

cat <<EOF >test.aib.yml
name: container_image
content:
  container_images:
    - source: registry.gitlab.com/centos/automotive/sample-images/demo/auto-apps
      tag: latest
      name: localhost/auto-apps
EOF

build --export tar --extend-define tar_paths='usr/share/containers/storage/overlay-images' test.aib.yml out.tar

tar xvf out.tar
cat usr/share/containers/storage/overlay-images/images.json | jq .[0].names[0] > image_names

assert_file_has_content image_names "localhost/auto-apps:latest"
