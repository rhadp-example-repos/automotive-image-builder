# Updating an OSTree-based image

Once you have booted an OSTree-based image, you can check the OSTree commit state and commit information using the following command:

```
ostree admin status
```

## Update the image.

Configure the OSTree image to not have a defined bootloader backend.

!!! note

    You only need to do this the first time.

```
ostree config set sysroot.bootloader none
ostree config set bootloader.backend none
```

## Build the OSTree update.

1. Edit the template to set the commit hash of the commit to update.

1. Build the repo.

```
make cs9-qemu-neptune-osbuild.repo
```

## Make the new commit available to the VM somewhere through apache.

1. The new commit is in repo directory called `cs9-qemu-neptune-osbuild.repo`.

1. Make the new commit available at _`http://ip_address/repo`_ by entering a command like the following:
```
dnf install httpd
systemctl start httpd
firewall-cmd --add-port=80/tcp
cp -r cs9-qemu-neptune-osbuild.repo /var/www/html/repo
```

## Update the VM.

* In the VM, ensure you can reach the repo with the new commit.

```
curl http://ip_or_domain/repo/
```

* Add a new remote pointing to the repo with the new commit.

```
ostree remote add --no-gpg-verify  upstream http://ip_address/repo/
```

* Make OSTree follow the new repo as shown in the following example, where _`upstream`_ is the name of the remote as defined above and _`cs9/x86_64/neptune`_
  is the ref created in manifest.

```
ostree admin switch upstream:cs9/x86_64/neptune
```

* Verify the new update has been pulled and deployed.

```
ostree admin status
```

* Reboot to upgrade to the next version of the image.

```
reboot
```
