# Short primer on OSTree

OSTree is a system designed to maintain and update immutable system
images. It is losely based on the git model, where each image you want
to track is a branch (sometimes called ref) in a repostitory with a
history of commits. The live system follows the branch, with a particular
commit checked out (called deployed) and booted into.

When the system updates, it pulls the latest commit from the branch of
the remote, and checks it out locally next to the currently deployed
commit. Then the system is restarted and now uses the new commit as
the active root. The old deployment is still available and you can
manually boot into it or change it back to be active (rollback). On
further updates, older versions may be removed to avoid unnecessary
disk use.

# Creating an OSTree repo

All the manifest support a `ostree` image type, and when you build
images based on this there are two stages. First an ostree commit is
created with all the content that should be part of the
image. Secondly a bootable system is created which is pulls and
deploys the newly created ostree commit into it.

If you want to use OSTree to update existing systems you need access
to the intermediate ostree commit. This is easily done by passing
the `OSTREE_REPO` variable to `make`, like this:

```
make cs9-qemu-minimal-ostree.x86_64.qcow2 OSTREE_REPO=ostree-repo
```

This will build the `cs9-qemu-minimal-ostree.x86_64.qcow2` image, and additionally
extract the ostree commits generated during the build and pull them into
the local ostree repo in a directory called `ostree-repo` (which will be created
if needed).

Additionally, when you do this the build will look at the current ersion of the
built ref in the repo (if there was a pre-existing one) and use that commit id as
the parent commit of the new image. This ensures that your ostree images have
an unbroken history in them.

Once the above command is run, you can inspect the ostree repo like this:

```
$ ostree refs --repo=ostree-repo
cs9/x86_64/qemu-minimal
$ ostree log --repo=ostree-repo cs9/x86_64/qemu-minimal
commit d80f713ecaf86e9ff2911811b8f97b3ae68c7e1403954e21628269edd7c2c95a
ContentChecksum:  0f0d7468b2476b164803e3552a388589eabc301cdba915cc4f6164a0ffda67e4
Date:  2022-03-30 14:14:02 +0000
Version: 9
(no subject)
```

Additionally if you boot the system in qemu and log in you can check the status:

```
# rpm-ostree status
State: idle
Deployments:
● auto-sig:cs9/x86_64/qemu-minimal
                   Version: 9 (2022-03-30T14:14:02Z)
                    Commit: d80f713ecaf86e9ff2911811b8f97b3ae68c7e1403954e21628269edd7c2c95a
```

Here we can see that there is only one ref installed (`cs9/x86_64/qemu-minimal`) that
has been installed from the remote called `auto-sig`. The commit installed is the one we just
built, and its marked active (the ●).

# Updating an OSTree-based image

As mentioned above, the image has a remote called `auto-sig`. You can see information for this
remote like this:

```
# ostree remote list -u
auto-sig  http://10.0.2.100/
```

This is the default url, which can be overridden by changing the `ostree_repo_url`. However, this particular
URL is very nice, because it matches what is used by the `runvm --publish-dir` feature. So, if you use
this to expose the `ostree-repo` directory created above to the VM, like so:

```
./runvm  --publish-dir=ostree-repo cs9-qemu-minimal-ostree.x86_64.qcow2
```

Then when you log in you can try to upgrade the system:

```
# rpm-ostree upgrade
1 metadata, 0 content objects fetched; 469 B transferred in 0 seconds; 0 bytes content written
No upgrade available.
```

It says there are no upgrades, because we're already on the latest version of the `cs9/x86_64/qemu-minimal` branch.
To create an update we could just build an image just like we did above, but that would also create a new image
which would replace the previously built one. To avoid this we build just the repo, although in real life you
probably want to build both.

We can do this like so:

```
$ make cs9-qemu-minimal-ostree.x86_64.repo DEFINES='extra_rpms=["curl"]'  OSTREE_REPO=ostree-repo
```

Note the `.repo` extension instead of `.qcow2`. Also, we specify an additional rpm in the new image, so that
we can see a difference when we update to the new version. As before we specify `OSTREE_REPO`, pointing it
at the same directory we did before.

Again, once the build is finished we can look at the resulting commit:

```
$ ostree log --repo=ostree-repo cs9/x86_64/qemu-minimal
commit 262e882d5c74da5315f712720529f599df415a1519f6efc1247edf96e148ac2c
Parent:  d80f713ecaf86e9ff2911811b8f97b3ae68c7e1403954e21628269edd7c2c95a
ContentChecksum:  e024335faba5db213e8c78cfc186de604d0921a82587696705364109789b4a86
Date:  2022-03-30 14:19:51 +0000
Version: 9
(no subject)

commit d80f713ecaf86e9ff2911811b8f97b3ae68c7e1403954e21628269edd7c2c95a
ContentChecksum:  0f0d7468b2476b164803e3552a388589eabc301cdba915cc4f6164a0ffda67e4
Date:  2022-03-30 14:14:02 +0000
Version: 9
(no subject)
```

As you can see we new have a new commit, which has a parent commit, making up a history of commits
for the branch.

In the VM you can now update to this, and check the status:

```
# rpm-ostree upgrade
15 metadata, 3 content objects fetched; 6220 KiB transferred in 2 seconds; 24.3 MB content written
Scanning metadata: 1821...done
Staging deployment...done
Run "systemctl reboot" to start a reboot

# rpm-ostree status
State: idle
Deployments:
  auto-sig:cs9/x86_64/qemu-minimal
                   Version: 9 (2022-03-30T14:19:51Z)
                    Commit: 262e882d5c74da5315f712720529f599df415a1519f6efc1247edf96e148ac2c

● auto-sig:cs9/x86_64/qemu-minimal
                   Version: 9 (2022-03-30T14:14:02Z)
                    Commit: d80f713ecaf86e9ff2911811b8f97b3ae68c7e1403954e21628269edd7c2c95a
# curl http://10.0.2.100/config
-bash: curl: command not found
```

We have not rebooted yet, so we can tell from the status that there are two deployments, and the
current one (the dot) is on the old one. At this point we can reboot (using e.g. `systemctl reboot`).
After boot things look like this:

```
# rpm-ostree status
State: idle
Deployments:
● auto-sig:cs9/x86_64/qemu-minimal
                   Version: 9 (2022-03-30T14:19:51Z)
                    Commit: 262e882d5c74da5315f712720529f599df415a1519f6efc1247edf96e148ac2c

  auto-sig:cs9/x86_64/qemu-minimal
                   Version: 9 (2022-03-30T14:14:02Z)
                    Commit: d80f713ecaf86e9ff2911811b8f97b3ae68c7e1403954e21628269edd7c2c95a
# curl http://10.0.2.100/config
[core]
repo_version=1
mode=archive-z2
```

The last command shows that curl is now available, and that it can access the ostree repository
at `10.0.2.100`.

# Further studies

This has only scratched the surface of OSTree and its companion rpm-ostree, once you are
at this point you can start learn about things like rollback and other administration details, or
the mechanics of how ostree works.

There are some details about [unattended updates](unattended_updates.md) in a separate doc.

For more information, see the [rpm-ostree docs](https://coreos.github.io/rpm-ostree/).
